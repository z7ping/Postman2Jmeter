import json
import os
from datetime import datetime
from .templates import JMETER_TEMPLATE
from urllib.parse import quote, urlparse, parse_qs

class Converter:
    def __init__(self):
        self.template = JMETER_TEMPLATE

    def parse_postman(self, collection_path, env_path=None):
        with open(collection_path, 'r', encoding='utf-8') as f:
            collection = json.load(f)
            
        variables = []
        if env_path:
            with open(env_path, 'r', encoding='utf-8') as f:
                env = json.load(f)
                variables = [{'name': v['key'], 'value': v['value']} 
                           for v in env.get('values', [])]
                
        requests = []
        def process_items(items, folder_name=""):
            for item in items:
                if 'item' in item:  # 这是一个文件夹
                    new_folder = f"{folder_name}/{item['name']}" if folder_name else item['name']
                    process_items(item['item'], new_folder)
                elif 'request' in item:  # 这是一个请求
                    try:
                        req = item['request']
                        url = req.get('url', {})
                        
                        # 处理URL
                        if isinstance(url, dict):
                            protocol = url.get('protocol', 'http')
                            # 处理 host
                            if isinstance(url.get('host'), list):
                                host = '.'.join(h.strip('{}') for h in url['host'])
                                domain = host
                            else:
                                domain = url.get('host', '')
                                
                            port = url.get('port', '')
                            # 处理 path
                            if isinstance(url.get('path'), list):
                                path = '/'.join(str(p).strip('{}') for p in url['path'])
                            else:
                                path = url.get('path', '')
                            
                            # 将查询参数分离出来，不再拼接到path中
                            query_params = []
                            if 'query' in url:
                                for param in url['query']:
                                    if param.get('disabled', False):
                                        continue
                                    if param.get('value') is not None:
                                        # 处理变量引用
                                        value = str(param['value']).replace('{{', '').replace('}}', '')
                                        query_params.append({
                                            'name': param['key'],
                                            'value': value
                                        })
                        else:
                            from urllib.parse import urlparse, parse_qs
                            try:
                                parsed = urlparse(url)
                                protocol = parsed.scheme or 'http'
                                domain = parsed.hostname or ''
                                port = str(parsed.port) if parsed.port else ''
                                path = parsed.path
                                # 解析查询参数
                                if parsed.query:
                                    params = parse_qs(parsed.query)
                                    query_params = [
                                        {'name': k, 'value': v[0]}
                                        for k, v in params.items()
                                    ]
                                else:
                                    query_params = []
                            except Exception:
                                protocol = 'http'
                                domain = 'localhost'
                                port = ''
                                path = ''
                                query_params = []

                        # 处理请求体
                        body = ''
                        if 'body' in req:
                            body_data = req.get('body', {})
                            if isinstance(body_data, dict):
                                if body_data.get('mode') == 'raw':
                                    body = body_data.get('raw', '')
                                elif body_data.get('mode') == 'formdata':
                                    form_data = []
                                    for form_item in body_data.get('formdata', []):
                                        if isinstance(form_item, dict) and not form_item.get('disabled', False):
                                            form_data.append(f"{form_item.get('key', '')}={form_item.get('value', '')}")
                                    body = '&'.join(form_data)
                        
                        # 处理请求头
                        headers = []
                        if 'header' in req:
                            header_list = req.get('header', [])
                            if isinstance(header_list, list):
                                for header in header_list:
                                    if isinstance(header, dict) and not header.get('disabled', False):
                                        headers.append({
                                            'name': header.get('key', ''),
                                            'value': header.get('value', '')
                                        })
                        
                        request_name = item.get('name', '')
                        request_data = {
                            'name': request_name,
                            'folder': folder_name,
                            'protocol': protocol,
                            'domain': domain,
                            'port': port,
                            'path': path,
                            'method': req.get('method', 'GET'),
                            'headers': headers,
                            'body': body,
                            'query_params': query_params
                        }
                        print(f"Adding request: {request_name} in folder: {folder_name}")
                        requests.append(request_data)
                    except Exception as e:
                        print(f"Error processing request {item.get('name', '')}: {str(e)}")
        
        if 'item' in collection:
            process_items(collection['item'])
        
        return {'variables': variables, 'requests': requests}

    def parse_apipost(self, collection_path):
        with open(collection_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n=== Starting ApiPost parsing ===")
        print(f"Found root keys: {data.keys()}")
        
        requests = []
        variables = []
        folders = {}  # 存储文件夹信息
        
        def build_folder_structure(items):
            print("\n=== Building folder structure ===")
            for item in items:
                if item.get('target_type') == 'folder':
                    folders[item['target_id']] = {
                        'name': item['name'],
                        'parent_id': item.get('parent_id', '0'),
                        'children': []
                    }
                    print(f"Found folder: {item['name']}")
        
        def get_folder_path(folder_id):
            if folder_id not in folders:
                return ''
            folder = folders[folder_id]
            parent_path = get_folder_path(folder['parent_id'])
            return f"{parent_path}/{folder['name']}" if parent_path else folder['name']
        
        def process_items(items):
            for item in items:
                print(f"\n=== Processing item: {item.get('name')} ===")
                print(f"Type: {item.get('target_type')}")
                
                if item.get('target_type') == 'api':
                    try:
                        request = item.get('request', {})
                        parent_id = item.get('parent_id', '0')
                        folder_path = get_folder_path(parent_id)
                        print(f"Folder path: {folder_path}")
                        
                        # 处理请求头
                        headers = []
                        if request and 'header' in request:
                            header_params = request['header'].get('parameter', [])
                            for header in header_params:
                                if isinstance(header, dict) and header.get('is_checked', 1) == 1:
                                    headers.append({
                                        'name': header.get('key', ''),
                                        'value': header.get('value', '')
                                    })
                            print(f"Headers: {headers}")

                        # 处理请求体
                        body = ''
                        query_params = []
                        if request:
                            print("\nProcessing request body:")
                            # 处理 body 参数
                            if 'body' in request:
                                body_type = request['body'].get('mode', '')
                                print(f"Body type: {body_type}")
                                
                                # 直接获取 raw 数据
                                raw_data = request['body'].get('raw', '')
                                if raw_data:
                                    body = raw_data
                                    print(f"Raw body: {body}")
                                # 如果没有 raw 数据，尝试处理 parameter
                                elif request['body'].get('parameter'):
                                    body_params = request['body']['parameter']
                                    if body_params:
                                        body_data = {}
                                        for param in body_params:
                                            if isinstance(param, dict) and param.get('is_checked', 1) == 1:
                                                body_data[param.get('key', '')] = param.get('value', '')
                                        if body_data:
                                            body = json.dumps(body_data)
                                        print(f"Parameter body: {body}")

                            print("\nProcessing query parameters:")
                            # 处理 query 参数
                            if 'query' in request and request['query'].get('parameter'):
                                query_list = request['query']['parameter']
                                for param in query_list:
                                    if isinstance(param, dict) and param.get('is_checked', 1) == 1:
                                        query_params.append({
                                            'name': param.get('key', ''),
                                            'value': str(param.get('value', ''))
                                        })
                                print(f"Query parameters: {query_params}")

                        # 处理 URL
                        url = item.get('url', '')
                        if not url.startswith('http'):
                            url = f"http://localhost{url if url.startswith('/') else f'/{url}'}"
                        
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        protocol = parsed.scheme or 'http'
                        domain = parsed.hostname or 'localhost'
                        port = str(parsed.port) if parsed.port else ''
                        path = parsed.path or ''
                        
                        print(f"\nURL details:")
                        print(f"Protocol: {protocol}")
                        print(f"Domain: {domain}")
                        print(f"Port: {port}")
                        print(f"Path: {path}")

                        request_name = item['name']
                        request_data = {
                            'name': request_name,
                            'folder': folder_path,
                            'method': item.get('method', 'GET'),
                            'protocol': protocol,
                            'domain': domain,
                            'port': port,
                            'path': path,
                            'body': body,
                            'headers': headers,
                            'query_params': query_params
                        }
                        print(f"\nFinal request data:")
                        print(json.dumps(request_data, indent=2))
                        requests.append(request_data)
                    except Exception as e:
                        print(f"Error processing request {item.get('name', '')}: {str(e)}")

                    # 递归处理子项目
                    if 'children' in item and item['children']:
                        process_items(item['children'])
                    if 'apis' in item and item['apis']:
                        process_items(item['apis'])

        # 开始处理
        if 'apis' in data:
            print(f"\nProcessing {len(data['apis'])} APIs from root")
            build_folder_structure(data['apis'])
            process_items(data['apis'])
        else:
            print("\nNo 'apis' field found in root")
            process_items(data)
        
        print(f"\n=== Processing complete ===")
        print(f"Total requests processed: {len(requests)}")
        return {'variables': variables, 'requests': requests}

    def convert_to_jmx(self, data, test_plan_name, output_path):
        print(f"Converting {len(data['requests'])} requests to JMX")  # 添加调试信息
        
        # 导入 groupby 过滤器
        from jinja2 import Environment, BaseLoader
        env = Environment(loader=BaseLoader())
        template = env.from_string(self.template)
        
        # 按文件夹分组处理请求
        requests_by_folder = {}
        for request in data['requests']:
            folder = request.get('folder', '')
            if folder not in requests_by_folder:
                requests_by_folder[folder] = []
            requests_by_folder[folder].append(request)
        
        # 渲染模板
        jmx_content = template.render(
            test_plan_name=test_plan_name,
            variables=data['variables'],
            folders=requests_by_folder.items()  # 传递分组后的数据
        )
        
        output_file = os.path.join(output_path, f"{test_plan_name}.jmx")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(jmx_content)
        
        print(f"JMX file saved to: {output_file}")  # 添加调试信息
        return output_file

    def parse_request(self, request):
        # 处理请求体
        body = ''
        if 'body' in request:
            if request['body'].get('mode') == 'raw':
                body = request['body'].get('raw', '')
            elif request['body'].get('mode') == 'formdata':
                form_data = []
                for form_item in request['body'].get('formdata', []):
                    form_data.append(f"{form_item['key']}={form_item.get('value', '')}")
                body = '&'.join(form_data)

    def parse_url(self, url):
        if isinstance(url, dict):
            protocol = url.get('protocol', 'http')
            domain = '.'.join(url['host']) if isinstance(url.get('host'), list) else url.get('host', '')
            port = url.get('port', '')
            path = '/'.join(url['path']) if isinstance(url.get('path'), list) else url.get('path', '')
            return protocol, domain, port, path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.scheme, parsed.hostname, parsed.port, parsed.path

def convert_to_jmx(source_type, collection_path, env_path, test_plan_name, output_path):
    converter = Converter()
    
    if source_type == 'postman':
        data = converter.parse_postman(collection_path, env_path)
    else:
        data = converter.parse_apipost(collection_path)
        
    return converter.convert_to_jmx(data, test_plan_name, output_path)

class CloudflareProxyMiddleware:
    def process_request(self, request, spider):
        if "feel-good-crawl.arslaancodes.com/?url=" in request.url:
            return None
        
        if request.meta.get('dont_proxy', False):
            return None
        
        original_url = request.url
        proxy_url = f'https://feel-good-crawl.arslaancodes.com/?url={original_url}'
        
        request.meta['original_url'] = original_url
        
        return request.replace(url=proxy_url)
    
    def process_response(self, request, response, spider):
        if 'original_url' in request.meta:
            return response.replace(url=request.meta['original_url'])
        
        return response

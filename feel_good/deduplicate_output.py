import json

seen_urls = set()
unique_lines = []

with open('output.jsonlines', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        url = data['url']
        
        if url not in seen_urls:
            seen_urls.add(url)
            unique_lines.append(line)

# Write deduplicated file
with open('output_deduped.jsonlines', 'w', encoding='utf-8') as f:
    for line in unique_lines:
        f.write(line)

print(f"Original: {len(seen_urls) + (len(open('output.jsonlines').readlines()) - len(unique_lines))} lines")
print(f"Deduplicated: {len(unique_lines)} lines")
print(f"Removed {len(open('output.jsonlines').readlines()) - len(unique_lines)} duplicates")
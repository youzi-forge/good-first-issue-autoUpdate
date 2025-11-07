from livereload import Server, shell

server = Server()
# Watch markdown and python build script
server.watch('good_first_issues.md', shell('python scripts/build_site.py'))
server.watch('scripts/build_site.py', shell('python scripts/build_site.py'))
# Serve _site folder
server.serve(root='_site', port=8000)


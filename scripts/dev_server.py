from livereload import Server

def rebuild():
    """Build the site using the same Python interpreter"""
    from build_site import main
    main()

# Ensure _site directory exists with initial build
rebuild()

server = Server()
# Watch files using the same Python interpreter
server.watch('good_first_issues.md', rebuild)
server.watch('scripts/build_site.py', rebuild)

# Serve _site folder
print("Development server running at: http://localhost:8000")
server.serve(root='_site', port=8000)


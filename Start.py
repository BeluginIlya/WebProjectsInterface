
import uvicorn
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

def run_webserver():
    try:
        from WebInterfaceForProjects import asgi
        uvicorn.run(asgi.application, host="0.0.0.0", port=8000)
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    run_webserver()

import uvicorn
import logging

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    uvicorn.run("main:app",
                host="0.0.0.0",
                port=20000,
                reload=True,
                forwarded_allow_ips="*",
                root_path="/api2")
if __name__ == '__main__':

    import os
    from app import app

    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))

    app.run(host=host, port=port)

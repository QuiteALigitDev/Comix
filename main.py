import flask, os, uuid, rarfile, subprocess, natsort, argparse
from urllib.parse import unquote, quote
from pathlib import Path
from flask import Flask, request, make_response, send_from_directory, redirect

DIR = ""

# Create an instance of the Flask class
app = Flask(__name__)

app.config["BASE_DIR"] = os.environ.get("BASE_DIR", "/home/sh")

DIR = app.config["BASE_DIR"]


@app.route("/client/<client_id>/<path:filename>")
def serve_client_file(client_id, filename):
    return send_from_directory(f"client/{client_id}", filename)

# Use the route() decorator to tell Flask what URL should trigger the function
@app.route("/browse/", defaults={"subpath": ""})
@app.route("/browse/<path:subpath>")
def hello_world(subpath):
    full_path = DIR + "/" + subpath
    client_id = request.cookies.get("client_id")
    if not client_id:
        client_id = str(uuid.uuid4())  # generate a new unique ID
        new_cookie = True
    else:
        new_cookie = False

    if os.path.isfile(full_path):
        subprocess.run(["rm", "-rf", f"client/{client_id}"])
        extention = os.path.splitext(full_path)[1]
        if extention == ".cbz":
            with rarfile.RarFile(full_path) as rf:
                rf.extractall(f"client/{client_id}")
            
            return redirect("/view?from=" + quote(full_path))

    dirlist = natsort.natsorted(os.listdir(full_path))
    parent = Path(full_path).parent

    html = """
    <head>
        <title>Browse - Comix</title>
    </head>
    <style>
        body { font-family:sans-serif; margin:20px; }
        a.folder { font-weight:bold; display:block; margin:5px 0; color:blue;             
            color: #090909;
            padding: 0.7em 1.7em;
            margin:10;
            font-size: 18px;
            border-radius: 0.5em;
            background: #e8e8e8;
            cursor: pointer;
            border: 1px solid #e8e8e8;
            transition: all 0.3s;
            text-decoration: none;}
        a.file { display:block; margin:5px 0; color:green; }
    </style>
    """

    html += f"<a class='folder' href='/browse/{os.path.relpath(parent, DIR)}'>...</a>"

    for direc in dirlist:
        html += f"<a class='folder' href='{request.path}/{direc}'>{direc}</a>\n"

    response = make_response(html)
    if new_cookie:
        response.set_cookie("client_id", client_id) 
    return response

@app.route("/view")
def view_images():
    client_id = request.cookies.get("client_id")
    back_path = request.args.get("from", "/browse/")
    back_path = unquote(back_path)

    base = f"client/{client_id}"

    if not os.path.exists(base):
        return "nothing here"

    images = sorted(
        f for f in os.listdir(base)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    )

    cur = os.path.basename(back_path)

    html = f"""   
    <head>
        <title>{cur} - Comix</title>
    </head>
    """

    html += """
    <style>
        body { margin:0; background:#000 }
        img {
            height:auto;
            width:85vw;
            display:block;
            margin:0 auto 20px;
        }
        a.Abutton{
            text-align:center;
            display:block;
            color: #090909;
            padding: 0.7em 1.7em;
            margin:10;
            font-size: 18px;
            border-radius: 0.5em;
            background: #e8e8e8;
            cursor: pointer;
            border: 1px solid #e8e8e8;
            transition: all 0.3s;
            text-decoration: none;
        }
        h2{
            color:white;
            text-align:center;
        }
    </style>
    """

    html += f"<h2>{cur}</h2>"

    images = natsort.natsorted(images)
    for img in images:
        html += f"<img src='/client/{client_id}/{img}'>"

    parent = Path(back_path).parent
    dirlist = natsort.natsorted(os.listdir(parent))


    html += f"<a class='Abutton' href='/browse/{str(parent).removeprefix(DIR)}/{dirlist[dirlist.index(cur) + 1]}'>FORWARD</a>"
    html += f"<a class='Abutton' href='/browse/{str(parent).removeprefix(DIR)}/{dirlist[dirlist.index(cur) - 1]}'>BACK</a>"

    return html 

def AddArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port to serve the local site.", required=False, type=int, default="8000")
    parser.add_argument("-d", "--dir", help="Directory to serve.", required=True, type=str)
    return parser.parse_args()

# Run the application (optional, but useful for running directly from the file)
if __name__ == '__main__':
    arguments = AddArgs()

    DIR = arguments.dir

    subprocess.run(["rm", "-rf", "client"])
    app.run(host="0.0.0.0", port=arguments.port, debug=True)

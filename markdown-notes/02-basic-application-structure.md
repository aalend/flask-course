# Basic application structure

Every Flask application must create an **application instance**. The web server passes all requests it receives from clients to this object for handling, using a protocol called the **Web Server Gateway Interface (WSGI)**. The application instance is an object of class `Flask`, usually created like this:

```python
from flask import Flask
app = Flask(__name__)
```

> [!WARNING]
> The module name is lowercase (`flask`); only the class is capitalized (`Flask`).
> Writing `from Flask import Flask` raises `ModuleNotFoundError: No module named 'Flask'`.

The only required argument to the `Flask` class constructor is the name of the main module or package of the application.

The `__name__` variable tells the Flask app where it is located, so Flask knows where to look for resources such as templates and static files. Think of it as a reference point to the application's files.

Clients such as web browsers send requests to the web server, which in turn sends them to the Flask application instance. The application instance needs to know what code to run for each requested URL, so it keeps a mapping of URLs to Python functions. The association between a URL and the function that handles it is called a **route**.

You define a route in Flask through the `app.route` decorator, exposed by the application instance. It registers the decorated function as a route.

## Routes and view functions

```python
@app.route('/')
def index():
    return '<h1>Hello World!</h1>'
```

Decorators are a standard Python feature. They can modify the behaviour of a function in different ways. A common use of decorators is to register functions as handlers for an event.

The example above registers the function `index()` as the handler for the application's root URL. If this application were deployed on a server like `example.com`, navigating to that website would trigger `index()` to run on the server. The return value, called a **response**, is what the client receives (if the client was a browser). Functions like `index()` are called **view functions**; what they return can be simple HTML or more complex content.

### Dynamic routes

URLs can have a parameter for dynamic routes. The portion enclosed in angle brackets is the **dynamic part**, so any URL that matches the static portion will be mapped to this route. When the function is called, Flask passes the dynamic component as an argument.

By default the dynamic part is a string, but it can be given a type. The route `/user/<int:id>` would match only URLs that have an integer in the `id` dynamic segment.

Flask's built-in converters:

| Converter | Accepts |
|-----------|---------|
| `string` (default) | any text **without** a slash `/` |
| `int` | positive integers |
| `float` | positive decimal numbers |
| `path` | like `string`, but **also** accepts slashes `/` |
| `uuid` | UUID strings |

Writing `<name>` with no type is implicitly `<string:name>`.

```python
@app.route('/user/<name>')
def user(name):
    return f'<h1>Hello {name.capitalize()}!</h1>'
```

## Server startup

```python
if __name__ == '__main__':
    app.run(debug=True)
```

The application instance has a `run` method that starts Flask's integrated development web server. The `__name__ == '__main__'` Python idiom ensures the development server starts **only when the script is executed directly**. When the script is imported by another script, it is assumed the parent will run a different server, so `app.run()` is skipped.

Once the server starts, it enters a loop that waits for requests and serves them. Several optional arguments can be passed to `app.run()` to configure the web server. During development it is good to enable debug mode by passing `debug=True`, which gives us a **debugger** and a **reloader** (the server restarts automatically when the code changes).

> [!NOTE]
> **Two ways to start the same dev server.** `app.run()` is one entry point; the Flask CLI is another. Both launch the same Werkzeug development server.
>
> | Approach | How you run it | Needs the `if __name__` block? |
> |----------|----------------|-------------------------------|
> | `app.run(debug=True)` | `uv run main.py` | yes |
> | `flask run --debug` | `uv run flask --app main run --debug` | no — the CLI finds the app itself |
>
> While learning, `app.run()` is perfectly fine. The `flask run` CLI is the more idiomatic choice later, especially once an application factory is used.

## Complete application

```python
from flask import Flask

# app instance
app = Flask(__name__)

# routes and view functions
@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

# http://127.0.0.1:5000/user/flask
@app.route('/user/<name>')
def user(name):
    return f'<h1>Hello {name.capitalize()}</h1>'

# run server
if __name__ == '__main__':
    app.run(debug=True)
```

To run the application, make sure the project's environment has Flask installed. From the terminal run `uv run main.py` and in the browser navigate to `http://127.0.0.1:5000`. If you type any other URL, the application will not know how to handle it and will return error code `404` to the browser.

> [!TIP]
> With `uv run` you don't need to manually activate the environment — it executes the command inside the project's environment for that single invocation.

To test the dynamic route, navigate to `http://127.0.0.1:5000/user/Alen`. The application responds with a customized greeting generated using the `name` dynamic argument. Try different names to see how the view function always generates the response based on the given name.

## The Request–Response Cycle

When Flask receives a request from a client (browser), it needs to make a few objects available to the view function that will handle it. The `request` object is a good example — it encapsulates the HTTP request sent by the client.

From `flask` we can import the `request` object. Flask uses **contexts** to temporarily make certain objects globally accessible. Thanks to contexts, view functions can be written like this:

```python
from flask import request

@app.route('/user-agent')
def check_user_agent():
    user_agent = request.headers.get('User-Agent')
    return f'Your browser is {user_agent}.'
```

Contexts enable Flask to make certain variables globally accessible **to a single thread without interfering with other threads**. In reality `request` cannot be a true global variable: in a multithreaded server the threads handle different requests from different clients at the same time, so each thread needs to see a different object in `request`.

### What is a thread?

A thread is the smallest sequence of instructions that can be managed independently. It is common for a process to have multiple active threads, sometimes sharing resources such as memory or file handles. A multithreaded web server starts a pool of threads and selects one from the pool to handle each incoming request.

### The two contexts

There are two contexts in Flask:

- the **application context**
- the **request context**

| Variable | Context | What it is |
|----------|---------|------------|
| `current_app` | application | the application instance for the active application |
| `g` | application | temporary storage during the handling of a request; reset with each request |
| `request` | request | encapsulates the contents of an HTTP request sent by the client |
| `session` | request | a dictionary the application can use to store values "remembered" between requests |

Flask activates these contexts before dispatching a request and removes them once the request is handled. When the application context is active, `current_app` and `g` become available to the thread; likewise, when the request context is active, `request` and `session` become available. If any of these variables are accessed **without** an active context, an error is raised.

### Seeing contexts in action

In the terminal where the project runs with `uv run main.py`, open a new tab and run `uv run python` to start a Python shell. Then:

```python
from main import app          # app is the application instance: app = Flask(__name__)
from flask import current_app # application context global

current_app.name              # RuntimeError: Working outside of application context.

app_ctx = app.app_context()
app_ctx.push()
current_app.name
# 'main'
app_ctx.pop()
```

The `RuntimeError` tells us we are working outside an application context, so we must activate one to access `current_app.name`.

> This typically means that you attempted to use functionality that needed
> the current application. To solve this, set up an application context
> with `app.app_context()`.

An application context is obtained by invoking `app.app_context()` on the application instance.

### Cleaner: use a `with` block

The manual `push()` / `pop()` pair works, but it is verbose and fragile — if you forget `pop()`, or an error is raised between `push` and `pop`, the context leaks (stays active). A `with` block solves this:

```python
with app.app_context():
    print(current_app.name)   # 'main'
# the context is automatically popped here, even if an error was raised inside
```

**Why this works.** A `with` block uses Python's **context manager** protocol. An object that supports it implements two hidden methods:

- `__enter__()` — runs once, on **entering** the block. Here it does `push()`.
- `__exit__()` — runs on **leaving** the block, on *any* exit (normal or via an exception). Here it does `pop()`.

`app.app_context()` returns such a context-manager object, so entering the block pushes the context and leaving it always pops it.

> [!TIP]
> The key benefit is not prettier code — it is **guaranteed cleanup**. Cleanup belongs in `__exit__` because that is the only one of the two methods that always runs at the end, no matter what happened inside the block. This is the same mechanism as `with open('file.txt') as f:`, where the file is guaranteed to close on exit.

## Request Dispatching

When the application receives a request from a client, it needs to find which view function to invoke. Flask looks up the request's URL in the application's **URL map**, which contains a mapping of URLs to the view functions that handle them. Flask builds this map using the `app.route` decorator, or the non-decorator version `app.add_url_rule()`.

To see it in motion, run `uv run python`:

```python
from main import app

app.url_map
```

Returns:

```python
Map([<Rule '/static/<filename>' (GET, OPTIONS, HEAD) -> static>,
     <Rule '/' (GET, OPTIONS, HEAD) -> index>,
     <Rule '/user-agent' (GET, OPTIONS, HEAD) -> check_user_agent>,
     <Rule '/user/<name>' (GET, OPTIONS, HEAD) -> user>])
```

The `/` and `/user/<name>` routes were defined by the `app.route` decorators in the application. The `/static/<filename>` route is a special route added by Flask to give access to static files. Notice how Flask maps each function to its route, so it knows which function to run.

The `HEAD`, `OPTIONS`, and `GET` elements shown in the URL map are the request methods handled by the route. Flask attaches methods to each route so that different request methods sent to the same URL can be handled by different view functions. The `HEAD` and `OPTIONS` methods are managed automatically by Flask, so in practice we say these routes are attached to the `GET` method.

## Request hooks

Sometimes it is useful to execute code before or after each request. At the start of each request it may be necessary to create a database connection or authenticate the user making the request. Instead of duplicating this code in every view function, Flask lets us register common functions to be invoked before or after a request is dispatched to a view function.

Request hooks are implemented as decorators. The three hooks supported by Flask are:

- `before_request` — register a function to run before each request.
- `after_request` — register a function to run after each request, if no unhandled exception occurred.
- `teardown_request` — register a function to run after each request, even if an unhandled exception occurred.

> [!WARNING]
> A fourth hook, `before_first_request`, existed in older Flask versions but was **deprecated in 2.2 and removed in 2.3.0** (current stable is 3.1.x). It no longer exists and will raise an error.
> It was commonly misused as a setup method. The modern approach is to run one-time setup when the application is **created**, not before the first request — that way the setup runs once up front instead of being checked against the request lifecycle, and the first user doesn't have to wait for it.

A common pattern for sharing data between request hook functions and view functions is the `g` context global. For example, a `before_request` handler can load the logged-in user from the database and store it in `g.user`; later, when the view function runs, it can read the user from there.

## Responses

When Flask calls a view function, it expects the return value to be the response to the request. In most cases the response is a simple string sent back to the client, like an HTML page.

But the HTTP protocol requires more than a string. An important part of the HTTP response is the **status code**, which Flask sets to `200` by default — the code indicating the request was carried out successfully.

When a view function needs to respond with a different status code, it can add the numeric code as a **second return value** after the response text. The following returns status code `400`, the code for a bad-request error:

```python
@app.route('/')
def index():
    return '<h1>Bad request!</h1>', 400
```

Responses can also take a **third value**, a dictionary of headers added to the HTTP response:

```python
@app.route('/')
def index():
    return '<h1>Bad request!</h1>', 400, {}
```

Instead of returning one, two, or three values as a tuple, a view function can return a **`Response` object**. The `make_response()` function takes one, two, or three arguments — the same values that can be returned from a view function — and returns a `Response` object. The following example creates a response object and then sets a cookie in it:

```python
from flask import make_response

@app.route('/')
def index():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response
```

### Redirects

There is a special type of response called a **redirect**. It does not include a page document; it just gives the browser a new URL from which to load a new page. A redirect is typically indicated with a `302` status code and the target URL given in a `Location` header. It can be generated with a three-value return or a `Response` object, but given its frequent use, Flask provides the `redirect()` helper:

```python
from flask import redirect

@app.route('/this-is-redirect')
def get_redirect():
    return redirect('https://google.com')
```

### Aborting with an error

Another special response is issued with the `abort()` function, used for error handling. The following returns status code `404` if the `id` dynamic argument does not represent a valid user:

```python
from flask import abort

@app.route('/user/<id>')
def get_user(id):
    user = load_user(id)
    if not user:
        abort(404)
    return f'<h1>Hello, {user}</h1>'
```

> [!NOTE]
> `abort()` does not return control to the view function — it raises an exception, so any code after it does not run.

---

> [!NOTE]
> **For later — the application factory pattern.**
> The code above uses the *global app* pattern (`app = Flask(__name__)` at module level), which is perfect while learning in a single file. As an application grows — multiple files, tests, blueprints — the global app starts causing friction (circular imports, harder testing). The fix is the **application factory**: wrap creation in a function that returns the app.
>
> ```python
> def create_app():
>     app = Flask(__name__)
>     # configuration, blueprint registration, one-time setup...
>     return app
> ```
>
> This also replaces the old `before_first_request` use case: one-time setup goes inside the factory. Pair it with the `flask run --app main:create_app` CLI. Not needed yet — revisit when the app outgrows one file.

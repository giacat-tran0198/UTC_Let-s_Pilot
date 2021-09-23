# Server

## Install library

`pip install -r requirements.txt`

## Start server

- Set environment:
    - Bask: `export FLASK_ENV=development`
    - CMD: `set FLASK_ENV=development`
    - Powershell: `$env:FLASK_ENV = "development"`
- Execute: `flask run`
- Initial database: `flask db init`
- Generate an initial migration: `flask db migrate -m "Initial migration."`
- Migration: `flask db upgrade`

# Server email

- Flask-Mailman [here](https://www.waynerv.com/flask-mailman/)

# Notification

## SSE - Client

### Registered

````js
const sse = new EventSource('/api/v1/users/stream?token=<token>');

sse.addEventListener(event, (event) => {
    console.log(JSON.parse(event.data))
})
````

### Disconnect

````js
window.onbeforeunload = (event) => {
    const e = event || window.event;
    // Cancel the event
    e.preventDefault();
    if (e) {
        e.returnValue = '';

        sse.close(); // close SSE in client before close tab/browser

        // Client notify the server that he quit the site
        axios.delete('/api/v1/users/stream', {
            headers: {'Authorization': 'Bearer ' + token}
        });
    }
    return '';
};
````

### Notify

1. Channel
    - open
    ````js
    sse.addEventListener('open', () => console.log('connected'));
      ````
    - error
    ````js
    sse.addEventListener('error', event => {
      console.log(event);
      if (eventSource.readyState === EventSource.CLOSED) {
        /* Traitement en cas de perte de connexion définitive avec le serveur */
      }
      if (eventSource.readyState === EventSource.CONNECTING) {
        /* En cas de perte de connexion temporaire avec le serveur */
      }
    });
    ````
    - action_project
    ````js
    sse.addEventListener('action_project', (event) => {
        console.log(JSON.parse(event.data))
    })
    ````

    - action_message: All user don't join in project that they will receive a notification message
    ````js
    sse.addEventListener('action_message', (event) => {
        console.log(JSON.parse(event.data))
    })
   ````

1. Data of the event `action_project`
    1. Schema
        ````typescript
        type data = {
          type: string;
          message: string;
          data?: object;
        };
        ````
    1. Type:
        - add_into_project:
            - _@{new_project.owner.username}' created a new project '{new_project.title}'. You are invited to join it._
              => schema of project item
            - _The new participant '@{user.username}' was added into the project '{project.title}'._ => schema of user
            - _You was invited into the project '{project.title}'._ => schema of project item
        - delete_project:
            - message: _The project '{older_project_title}' was removed by '@{owner_username}'._ =>
              data:
              ````typescript
                {
                    project_id : int;
                    project_title: str; // older project title
                }
              ````
        - edit_project:
            - _The title's project '{older_project_title}' become the new tilte '{project.title}'._ =>
              data:
              ````typescript
              {
                project_id: int;
                project_title: str; // new project title
              }
              ````
            - _'@{current_user.username}' left the project'{project.title}'._ => data:
              ````typescript
              {
                user_id: int; // user left id
                project_id: int;
                project_title: str
              }
              ````
            - _You was designated new coach in the project '{project.title}'._ =>
              data:
              ```typescript
              {
                project_id: int; // project id for our new coach
                project_title: str;
              }
              ```
            - _'@{user.username}' was designated new coach in the project '{project.title}'._ =>
              data:
              ````typescript
              {
                user_id: int; // new coach id
                project_id: int;
                project_title: str;
              }
              ````
            - _You was withdrawn from coach in the project '{project.title}'._ =>
              data:
              ````typescript
              {
                project_id: int; // project id for be withdrawn
                project_title: str;
              }
              ````
            - _'@{user.username}' was withdrew from coach, he will be a participant the project'{project.title}'._ =>
              data:
              ````typescript
              {
                user_id: int; // older coach id
                project_id: int;
                project_title: str;
              }
              ````
            - _You was removed in the project '{project.title}'._ => data:
              ````typescript
              {
                project_id: int; // project id for be removed
                project_title: str;
              }
              ````
            - _'@{participant.username}' was removed in the project '{project.title}'._ =>
              data:
              ````typescript
              {
                user_id: int; // older_participant_id
                project_id: int;
                project_title: str;
              }
              ````

1. Data of the event `action_message`
    1. Schema
        ````typescript
        type object = {
          type: string;
          message: string;
          data?: object;
        };
        ````
    1. Type:
        - new_message:
            - _'@{message.sender.username}' sent a new message._ => data: `{project_title: project.title}`
            - _'@{message.sender.username}' sent you a new private message._ => data: `{project_title: project.title}`

1. Data of the event `action_user`:
    1. Schema: Same the other event
    1. Type:
        - admin_user:
            - _You become an admin._ => data: `{user_id: int, admin: bool}`
            - _You become a normal._ => data: `{user_id: int, admin: bool}`
        - archive_user:
            - _You was archived._ => data: `{user_id: int, archive: bool}`
            - To ***unarchive*** => Server will send an email.

## Webpush

### Document

Webpush only works when activated by **client** and for *offline user* (He not connect the app. The notification will
show in OS)

The **Push Subscription json generated** will be stored in **redis and DB**, server will transfer data from DB to redis.
Must *remove* the **Service Worker** in browser before the test.

- [doc1](https://techonometrics.com/posts/web-push-notifications-basic-functionality-using-flask-backend/)
- [doc2](https://raturi.in/blog/webpush-notification-using-python-and-flask/)
- get key public and private [here](https://web-push-codelab.glitch.me)

### Schema data:

The schema is similar to *SSE*

````typescript
type schema = {
    type: str;
    data: {
        type: str;
        message: str;
        data?: object;
    }
}
````

# SocketIo

## Install

Add socketio for reactjs: `yarn add socket.io-client`

## Connect

````js 
const socket = socketIOClient('/ws/messages', {
    extraHeaders: {
        Authorization: "Bearer authorization_token_here"
    }
});
socket.on('connect', () => console.log('connect'));
socket.on('connect_error', (e) => {
    console.log("connect_error")
    console.log(e)
});
````

## Error

````js
socket.on('error', function (e) {
    console.log("error")
    console.log(e)
});
````

## Join/Leave the project

When the member goes into(out) the meeting, he must joins(leaves) the project

Schema data of callback (list user online in project) in `join_project`: `array({'user_id': int})`

````js
socket.emit('join_project', {project_id: int},
    (data) => console.log(data));
socket.emit('leave_project');
````

Notify one user join/leave the project

Schema data: `{'user_id': int}`

````js
socket.on('online', (data) => console.log(data));
socket.on('offline', (data) => console.log(data));
````

## Send/Receive message in the project

- `content` or `file_name && file_base64` must be required
- `file_name` has extensions: txt, pdf, png, jpg, jpeg, gif, doc. File's size maximum depends on encoding base64 of
  capability's browser

````js
socket.emit('send_message', {
    'project_id': int,
    'content': str,
    'file_name': str,
    'file_base64': str,
    'receiver_id': int / null
}, (data) => console.log(data));
socket.on('receive_message', function (data) {
    console.log(data)
});
````

Use `FileReader` to get file in client

````js
var selectedFile;
const changeHandler = (event) => {
    selectedFile(event.target.files[0]);
};

const handleSubmission = () => {
    var fileReader = new FileReader();
    fileReader.readAsDataURL(selectedFile)
    fileReader.onload = () => {
        var arrayBuffer = fileReader.result;
        socket.emit('send_message', {
            'project_id': 5,
            'sender_id': 1,
            'file_name': selectedFile.name,
            'file_base64': arrayBuffer
        })
    }
}
````

- Schema receive message

````js
{
    content: str
    file_name: str
    file_base64: str
    created_at: str // "08/06/2021, 22:58"
    id: int
    sender: {
        email: str
        first_name: str
        id: int
        last_name: str
        username: str
    }
    receiver: null | {
        email: str,
        first_name: str,
        id: int,
        last_name: str,
        username: str,
    }
}
````

- For image: `<img src={data.file_base64} alt={data.file_name}/>`
- For file download: `<a href={data.file_base64} download>Download</a>`
# Table of Contents

- [TaskTracker Server](#tasktracker-server)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Database generation](#database-generation)
  - [Models](#models)
    - [TaskTracker files](#TaskTracker-files)
    - [Activity Tracker files](#activity-tracker-files)

# TaskTracker Server

The TaskTracker server is part of the TaskTracker toolkit for collecting and processing data of student activity during problem solving. TaskTracker server facilitates interaction with the [TaskTracker plugin](https://github.com/JetBrains-Research/task-tracker-plugin).

The primary goal of this project is data collection. First, tracking and analysis of students’ coding behavior can be a valuable source of insight into the learning process: for example, help the teacher to improve their course and understand which topics and assignments may be more difficult for students. Second, such data may be used in computing education research. If you choose to share your problem-solving data with us, it will help our studies in generating personalized hints during problem solving.

For more information about TaskTracker, consult the following resources:
- [wiki](https://github.com/JetBrains-Research/task-tracker-server/wiki)
- [research paper](https://arxiv.org/abs/2012.05085)
- [presentation](https://github.com/JetBrains-Research/task-tracker-server/blob/master/images/TaskTracker.pdf)
- [demo](https://www.youtube.com/watch?v=ZZXmiFCAgTI).


---

## Requirements

1. [MongoDB](https://www.mongodb.com/)
2. [Node.js](https://nodejs.org/en/)
3. [npm](https://www.npmjs.com/)

---

## Installation

1. Download the repository.
2. Run [MongoDB](https://www.mongodb.com/). It has to work on the `localhost:27017`.
3. Install TaskTracker packages by issuing `install npm` as root from the server installation directory:
  ```
  sudo install npm
  ```
   
4. Issue `npm start` as root from the server installation directory. It will work on `localhost:3000`.

If everything is done correctly, you will see the following message:

<img src="images/server_running_example.png" width="800">

---

## Database generation

The data for the database can be found in [configs](/configs/task-tracker-sources).
You can [change the data](https://github.com/JetBrains-Research/task-tracker-server/wiki/Update-texts-and-tasks) before generating the database. 

To generate a database for the [TaskTracker plugin](https://github.com/JetBrains-Research/task-tracker-plugin), send the `POST` request to `<path_to_your_server>/api/database-generator/task-tracker`.

Every time you [change the configs](https://github.com/JetBrains-Research/task-tracker-server/wiki/Update-texts-and-tasks), re-generate the database.

**Note**: The default `<path_to_your_server>` is `localhost:3000`.

See an example using [Postman](https://www.postman.com/):

<img src="./images/postman_example.png">

---

## Models

The section describes the models and API operations in the server. 
For a complete description of all models, see the [API reference](https://github.com/JetBrains-Research/task-tracker-server/wiki/API) in the wiki.

### TaskTracker files

The `data-item` model stores code snapshots of user solutions from the associated [TaskTracker plugin](https://github.com/JetBrains-Research/task-tracker-plugin).

#### Model

Field | Type | Description
---   | --- | ---
`id` |  String | Internal MongoDB [ObjectId](https://docs.mongodb.com/manual/reference/method/ObjectId/).
`externalDiId` |  Integer | External ID represented in public fields as `id`.
`codePath` |  String | Path to the file with code snapshots.
`activityTrackerKey` |  String | External ActivityTracker item ID.

#### Operations

Endpoint | Method | Description
---   | --- | --- 
`/api/data-item`    | `POST` | Save a TaskTracker file with code snapshots in the database.
`/api/data-item/all`| `GET`  | Get metadata for all TaskTracker files.
`/api/data-item/:id`| `GET`  | Get metadata for a TaskTracker file by its external ID.

**Note**: For more information, see [data item operations](https://github.com/JetBrains-Research/task-tracker-server/wiki/API:-Data-item#operations) in the wiki.


### Activity Tracker files

The `activity-tracker-item` model stores Activity Tracker logs with user actions from the associated [TaskTracker plugin](https://github.com/JetBrains-Research/task-tracker-plugin).

#### Model

Field | Type | Description
---   | --- | ---
`id` |  String | Internal MongoDB [ObjectId](https://docs.mongodb.com/manual/reference/method/ObjectId/).
`externalAtiId` |  Integer | External ID collected from the file `id` in public fields.
`codePath` |  String | Path to the Activity Tracker log.
`createdAt` |  Date | Creation date.

#### Operations

URL | Type | Description
---   | --- | --- 
`/api/activity-tracker-item`    | `POST` | Save an Activity Tracker log in the database.
`/api/activity-tracker-item/all`| `GET`  | Get metadata for all Activity Tracker logs.
`/api/activity-tracker-item/:id`| `GET`  | Get metadata for an Activity Tracker log by its external ID.

  **Note**: For more information, see [Activity Tracker operations](https://github.com/JetBrains-Research/task-tracker-server/wiki/API:-Activity-tracker-item#operations) in the wiki.

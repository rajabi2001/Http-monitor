# Http-monitor
A HTTP endpoint monitor service written in python with Flask.


## Database

#### Tables : 

**Users:**

| id(pk)  | created_at | updated_at | deleted_at | username     | password     |
| :------ | ---------- | ---------- | ---------- | ------------ | ------------ |
| integer | datetime   | datetime   | datetime   | varchar(255) | varchar(255) |

**URLs:**

| id(pk)  | created_at | updated_at | deleted_at | user_id(fk) | address      | threshold | failed_times |
| ------- | ---------- | ---------- | ---------- | ----------- | ------------ | --------- | :----------- |
| integer | datetime   | datetime   | datetime   | integer     | varchar(255) | integer   | integer      |

**Requests:**

| id(pk)  | created_at | updated_at | deleted_at | url_id(fk) | result  |
| ------- | ---------- | ---------- | ---------- | ---------- | ------- |
| integer | datetime   | datetime   | datetime   | integer    | integer |

## API

### Specs:

For all requests and responses we have `Content-Type: application/json`.

Authorization is with JWT.

#### User endpoints:

**Login:**

`POST /api/users/login`

request structure: 

```
{
	"username":"foo", // alpha numeric, length >= 4
	"password":"*bar*" // text, length >=4 
}
```

**Sign Up:**

`POST /api/users`

request structure (same as login):

```
{
	"username":"foo", // alpha numeric, length >= 4
	"password":"*bar*" // text, length >=4 
}
```

#### URL endpoints:

**Create URL:**

`POST /api/urls`

request structure:

```
{
	"address":"http://some-valid-url.com" // valid url address
	"threshold":20 // url fail threshold
}
```

##### **Get user URLs:**

`GET /api/urls`

**Get URL stats:**

`GET /api/urls/:urlID?from_time&to_time`

`urlID` a valid url id


**Get URL alerts:**

`GET /api/alerts`

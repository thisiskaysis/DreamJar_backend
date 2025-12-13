# Crowdfunding Back End
DreamJar

## Planning:
### Concept/Name
A crowdfunding website for children.
Parents create user accounts.
Each Parent can create Children.
For each Child, Parent can create a campaign for their Child.

### Intended Audience/User Stories
{{ Who are your intended audience? How will they use the website? }}

### Front End Pages/Functionality
- {{ A page on the front end }}
    - {{ A list of dot-points showing functionality is available on this page }}
    - {{ etc }}
    - {{ etc }}
- {{ A second page available on the front end }}
    - {{ Another list of dot-points showing functionality }}
    - {{ etc }}

### API Spec
#### Public Endpoints

| URL | HTTP Method | Purpose | Request Body | Success Response Code | Authentication/Authorisation |
| --- | ----------- | ------- | ------------ | --------------------- | ---------------------------- |
| /campaigns/ | GET | Browse all campaigns | N/A | 200 OK | Public |
| /campaigns/{id} | GET | View campaign details | N/A | 200 OK | Public |
| /campaigns/{id}/donations | GET | View campaign's donations | 200 OK | Public |
| /campaigns/{id}/donations | POST | Make a donation (with or without a user account) | 201 Created | Public |

### DB Schema
![]( {{ ./relative/path/to/your/schema/image.png }} )
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
- **Log in page**
    - Sign in with Email & Password
    - Sign in with Google
  
- **Profile Page**
    - Create Child/ren
    - Create campaigns under each child
    - List all campaigns under each child
    - Update/Delete profile
    - Update/Delete child
    - Update/Delete campaign
    - Track campaign data
      - Total raised to date
      - Percentage of goal reached
      - How many donations have been received
      - Time remaining (if deadline)
  
- **Campaigns**
     

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
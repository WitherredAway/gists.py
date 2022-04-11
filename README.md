# gists.py

A simple asynchronous python wrapper for the [GitHub Gists](https://docs.github.com/en/rest/reference/gists) API
----------

## Features
*All unchecked features are planned*
### Gists
- [ ] `GET`ing from `/gists`, to get authenticated user's Gists
- [ ] `GET`ing from `/users/{username}/gists` to get a user's Gists
- [ ] `GET` ing from `/gists/public` to get public Gists
- [ ] `GET` ing from `/gists/starred` to get authenticated user's starred Gists
- [X] `POST`ing to `/gists`, to create a Gist
- [X] `GET` ing from `/gists/{gist_id}` to get a Gist
- [X] `PATCH`ing to `/gists/{gist_id}`, to edit a Gist
- [X] `DELETE`ing from `/gists/{gist_id}` to delete a Gist
### Gists - Forks
- [ ] `POST`ing to `/gists/{gist_id}/forks` to fork a Gist to the authenticated user's profile
### Gists - Star
- [ ] `GET`ing from `/gists/{gist_id}/star` to check if a gist is starred by the authenticated user
- [ ] `PUT`ing `/gists/{gist_id}/star` to star a Gist with the authenticated user
- [ ] `DELETE`ing from `/gists/{gist_id}/star` to unstar a Gist with the authenticated user
### Gists - Comments
- [ ] `GET`ing from `/gists/{gist_id}/comments` to get all comments on a Gist
- [ ] `POST`ing to `/gists/{gist_id}/comments` to create a comment on a Gist
- [ ] `GET`ing from `/gists/{gist_id}/comments/{comment_id}` to get a comment on a Gist
- [ ] `PATCH`ing to `/gists/{gist_id}/comments/{comment_id}` to edit a comment of the authenticated user on a Gist
- [ ] `DELETE`ing from `/gists/{gist_id}/comments/{comment_id}` to delete a comment of the authenticated user on a Gist

## Installation
```sh
pip install gists.py
```
or
```sh
pip install git+https://github.com/WitherredAway/gists.py
```

## Usage examples
*This section is a work in progress*

### Import gists and instantiate a client
```py
# Import asyncio
import asyncio
# Import the package
import gists

# Create a client instance
client = gists.Client("YOUR GITHUB PERSONAL ACCESS TOKEN")
```
### Create a new gist
```py
async def main_create() -> gists.Gist:
    # The description to set
    description = "Hi this is a gist"

    # The files to create in the gist

    # Format:
    # 
    # files = {
    #     'name_of_the_file.extension': {
    #         'filename': "name_of_the_file.extension",
    #         'content': "content_of_the_file"
    #         }
    #     }

    files = {
        'example.txt': {
            'filename': "example.txt",
            'content': "I like turtles"
            },
        'helloworld.py': {
            'filename': "helloworld.py",
            'content': "print(\"Hello, world\")"
            }
        }
    # Whether or not the gist should be public
    public = True

    # This method creates a new gist and returns a Gist object associated with that gist
    gist = await client.create_gist(files, description=description, public=public)
    return gist
        
# Run the main_create() function
gist_1 = asyncio.run(main_create())
# Print the gist's id
print(gist_1.id)
```
### Get a gist
```py
async def main_get():
    # This method fetches the gist associated with the provided gist id, and returns a Gist object
    gist = await client.get_gist(gist_1.id)
    return gist

# Run the main_get() function
gist_1 = asyncio.run(main_get())
# Print the gist's description
print(gist_1.description)
```
### Edit gist using the edit method of a Gist object
```py
async def main_edit():
    # The description to edit to
    description = "Hello this is a gist, but edited"

    # The files to edit in gist

    files = {
        # Use an existing filename to edit that file
        'example.txt': {
            'filename': "example.txt",
            'content': "I like turtles and dogs"
        },
        # Edit the filename of an existing file
        # 
        # Format:
        # 'old_name_of_the_file.extension': {
        #     'filename': "new_name_of_the_file.extension",
        #     'content': "content_of_the_file"
        #     }
        'helloworld.py': {
            'filename': "hellouniverse.py",
            'content': "print(\"Hello, universe\")"
        },
        # Create a new file by providing a new filename
        'newfile.txt': {
            'filename': "newfile.txt",
            'content': "This is a new file"
        }
    }
    await gist_1.edit(files=files, description=description)
    
# Run the main_edit() function
asyncio.run(main_edit())
# Print the gist's edited description
print(gist_1.description)
```

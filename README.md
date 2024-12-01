## Simple Membership System
## Configuration

1. **Set up MySQL Database & Database Connection:**
    - Open XAMPP
    - Create a new MySQL database.
    - Open `model.py`.
    - Update the configuration to match your MySQL setup

## How to Run

1. **Start the server:**

      ```sh
      flask run
      ```

## Pull Request Procedure

1. **Create a branch:**

      ```sh
      git checkout -b feat/steph-be
      ```
2. **Commit Changes:**

      ```sh
      git commit -m "message"
      ```
3. **Pull from main:**

      ```sh
      git pull origin main
      ```
4. **Push branch:**

      ```sh
      git push -u origin your-branch
      ```
5. **Pull Request:**
    - Go to github repo and click the pull request menu
    - Click the new pull request button
    - Select the branch
    - Create pull request
6. **Pull Request:**
    - Go to github repo and click the pull request menu
    - Click the new pull request button
    - Select the branch
    - Create pull request
7. **Merge Pull Request**

## Import Function From Another Module
1. **Make it into a module**
    - Make a `__init__.py` file in the respective folder
    - In the `__init__.py` file add an `__all__` statement
    - In `__all__` adds all the function you need such as `__all__ = [first_file, second_file]`
    - Now you can import that respective file into your other files using `from file_function import *`
    - To call your function you need to use `file_name.function`
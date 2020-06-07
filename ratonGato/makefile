all:
	@echo "Tags:\n"
	@echo"start\t\tMakes migrations, migrates, collects static files, and runs server\n"
	@echo "clean\t\tRemoves .pyc files and staticHeroku folder\n"
	@echo "restart\t\tCleans and starts again"

####### Constants #######
PSI_4_DIR := ~/psi_p4/ratonGato #Substitute for absolute path in device if needed

####### Auxiliar functions #######
remove_file_recursive:
	@cd $(DIRECTORY); \
	find . -name "$(EXTENSION)" -type f -delete

remove_folder_recursive:
	@cd $(DIRECTORY); \
	find -name "$(DIRECTORY_NAME)" -type d -prune -exec rm -rf {} \;

####### Main tags #######
start:
	@python3 manage.py makemigrations
	@python3 manage.py migrate
	@python3 manage.py collectstatic
	@python3 manage.py runserver

clean:
	@make -s remove_file_recursive EXTENSION="*.pyc" DIRECTORY=$(PSI_4_DIR)
	@make -s remove_folder_recursive DIRECTORY_NAME="__pycache__" DIRECTORY=$(PSI_4_DIR)
	@make -s remove_folder_recursive DIRECTORY_NAME=".idea" DIRECTORY=$(PSI_4_DIR)
	@make -s remove_file_recursive EXTENSION="db.sqlite3" DIRECTORY=$(PSI_4_DIR)
	@make -s remove_file_recursive EXTENSION=".coverage" DIRECTORY=$(PSI_4_DIR)
	@make -s remove_folder_recursive DIRECTORY_NAME="staticHeroku" DIRECTORY=$(PSI_4_DIR)

restart:
	@make -s clean
	@make -s start

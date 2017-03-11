#include <crypt.h>
#include <stdio.h>

char salt[] = "Peter_Is_Gay";

int main(int argc, char* argv[]){
	char* password = crypt("Bitch", salt);
	char* decrypt = crypt(password, salt);
	printf("%s", password);
	printf("%s", decrypt);
	
	return 0;
}

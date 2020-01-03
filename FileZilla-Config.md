# FileZilla configurations
In order to ensure proper workflow make the following configurations:
* Edit FTP users **Edit->Users**:
![Edit-Users](screenshots/edit-users.JPG)
* Add new user, dont forget a password **Edit->Users->General->Add**:
![New-User](screenshots/add-user.JPG)
* Add a folder which you'll share: **Edit->Users->Shared Folders->Add**:<br>
Add a user which can access this folder:
![Share-Folder-User](screenshots/share-folder---add-user.JPG)
<br>After choosing a folder, configure user access rights like on screenshot:
![Share-Folder](screenshots/share----folder.JPG)<br>
* Configure FTP over TLS **Edit->Settings->FTP over TLS settings**:
![FTP-TLS](screenshots/ftp-over-tls.JPG)<br>
		
		1. Generate new certificate and choose it.
		2. Enable FTP over TLS.
		3. Allow explicit FTP over TLS.
		4. Choose a port you want to use.
		5. Check Force PROT P to encrypt file transfers when using FTP over TLS.
		6. Uncheck Require TLS session resumption on data connection when using PROT P.
* Configure Passive mode settings **Edit->Settings->Passive mode settings**:
![PASV](screenshots/pasv.JPG)<br>
Check **Use custom port range** and choose desired ports for passive mode.
		

# Frequently made mistakes

### Pointing volatility to a directory containing symbol json files
You have your ISF files in `/some/folder`. So now all you gotta do to make volatility use them is pass `-s /some/folder` to `vol`, right?
**WRONG!** You have to put your symbol files into `/some/folder/<operating-system>` (e.g. `/some/folder/linux`) and pass `-s /some/folder` to `vol`.




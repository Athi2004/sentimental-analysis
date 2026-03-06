# Fix Video Not Showing in Post

## Tasks
- [x] Update Post model: change video_path to media_path and add media_type column
- [x] Update upload route: detect file type (video/image) and set media_type
- [x] Update delete route: use media_path instead of video_path
- [x] Test the changes by uploading a video and checking if it displays in the feed

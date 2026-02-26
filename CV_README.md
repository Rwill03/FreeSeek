# ⚠️ CV FILE REQUIRED

You need to add your CV/resume file to this location.

## Instructions:

1. **Prepare Your CV**
   - Format: PDF (recommended)
   - File name: `cv.pdf`
   - Keep it professional and up-to-date
   - Ensure it's readable and well-formatted

2. **Place Your CV**
   - Copy your CV to the project root: `/Users/f.w.e/Documents/Projects/FreeSeek/cv.pdf`
   - Or update the path in `.env`:
     ```
     CV_FILE_PATH=/path/to/your/cv.pdf
     ```

3. **Verify**
   - Make sure the file exists at the specified path
   - Test that it's a valid PDF
   - The system will upload this file when applying to jobs

## Example:
```bash
# From project root
cp ~/Documents/my-cv.pdf ./cv.pdf
```

## Alternative Locations:
If you prefer to keep your CV elsewhere, update `.env`:
```
CV_FILE_PATH=/Users/yourusername/Documents/cv.pdf
```

**The application will NOT work without a valid CV file!**

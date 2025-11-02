import express from 'express';
import multer from 'multer';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const upload = multer({ storage: multer.memoryStorage() });

app.use(cors());
app.use(express.json({ limit: '50mb' }));

app.post('/rename', upload.array('files'), (req, res) => {
    try {
        const preview = JSON.parse(req.body.preview);

        if (!req.files || req.files.length === 0) {
            return res.status(400).json({ error: 'No files provided' });
        }

        const uploadDir = path.join(__dirname, 'renamed_images');
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }

        let successCount = 0;
        req.files.forEach((file, index) => {
            const newName = preview[index].new;
            const filePath = path.join(uploadDir, newName);

            fs.writeFileSync(filePath, file.buffer);
            successCount++;
        });

        res.json({
            success: true,
            count: successCount,
            message: `Renamed ${successCount} files successfully`
        });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});

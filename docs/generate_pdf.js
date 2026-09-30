const puppeteer = require('puppeteer');
const path = require('path');

async function generatePDF(htmlFile, pdfFile) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    const filePath = `file://${path.join(__dirname, htmlFile)}`;
    
    await page.goto(filePath, { waitUntil: 'networkidle0' });
    await page.pdf({ 
        path: pdfFile, 
        format: 'A4',
        printBackground: true,
        margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' }
    });
    
    await browser.close();
    console.log(`Generated ${pdfFile}`);
}

(async () => {
    try {
        await generatePDF('cotizacion.html', 'cotizacion_tapi.pdf');
        await generatePDF('presentacion_legal.html', 'presentacion_legal_tapi.pdf');
        console.log('PDFs generated successfully!');
    } catch (e) {
        console.error('Error generating PDFs:', e);
    }
})();

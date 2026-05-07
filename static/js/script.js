document.getElementById('predictForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('submitBtn');
    const display = document.getElementById('resultDisplay');
    
    // 1. CLEAR PREVIOUS RESULT INSTANTLY
    // This ensures that even if the request is slow, the old result disappears
    display.innerHTML = "";
    display.classList.add('hidden');
    
    // 2. Button Loading State
    btn.innerText = "ANALYZING SENSORS...";
    btn.disabled = true;

    // 3. Collect Form Data
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Prediction failed');
        
        const res = await response.json();

        // 4. RE-RENDER FRESH HTML
        display.classList.remove('hidden');
        display.innerHTML = `
            <div class="result-card" style="border-color: ${res.result_color}">
                <h3 style="color: #666; font-size: 0.7rem; margin:0;">GENERAL HEALTH STATUS</h3>
                <h2 style="color: ${res.result_color}; margin: 5px 0;">${res.status}</h2>
                <p style="font-size: 0.8rem; margin:0;">Health Confidence: <strong>${res.health_conf}</strong></p>
                <div class="meter-bg">
                    <div class="meter-fill" style="width: ${res.health_conf}; background: ${res.result_color};"></div>
                </div>

                ${res.diagnosis ? `
                    <div class="diag-alert animate-pulse">
                        <p style="color: #ff4b2b; font-size: 0.7rem; margin-bottom: 5px;">SPECIFIC DIAGNOSIS</p>
                        <h1 style="color: #fff; font-size: 1.3rem; margin: 0;">${res.diagnosis}</h1>
                        <p style="font-size: 0.8rem; margin-top: 10px;">Diagnostic Confidence: <strong>${res.diag_conf}</strong></p>
                        <div class="meter-bg">
                            <div class="meter-fill" style="width: ${res.diag_conf}; background: #ff4b2b;"></div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

    } catch (err) {
        console.error(err);
        display.classList.remove('hidden');
        display.innerHTML = `<div class="result-card" style="border-color: gray;">
                                <h2 style="color: gray;">Error Connecting to AI</h2>
                             </div>`;
    } finally {
        // 5. Reset button regardless of outcome
        btn.innerText = "RUN DIAGNOSTIC";
        btn.disabled = false;
    }
});

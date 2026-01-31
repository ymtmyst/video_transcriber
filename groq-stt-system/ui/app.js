document.addEventListener('DOMContentLoaded', () => {
    console.log("App.js loaded - v1.2 (Enhanced Normalization)");
    const overlay = document.getElementById('stt-overlay');
    const canvas = document.getElementById('waveform');
    const ctx = canvas.getContext('2d');

    // Handle high-DPI displays
    const dpr = window.devicePixelRatio || 1;
    function resizeCanvas() {
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // State
    let isRecording = false;
    let animationId;
    let currentLevel = 0;
    let targetLevel = 0;
    
    // Improved Adaptive Normalization State
    let maxVolume = 0.05; // Start with reasonable baseline
    let smoothedLevel = 0; // For envelope following
    let recentPeaks = []; // Track recent peaks for better normalization
    const MAX_PEAKS_HISTORY = 30; // ~0.5 seconds of history at 60fps
    
    // Envelope Follower Config
    const ATTACK_COEF = 0.3;  // Fast attack (react quickly to loud sounds)
    const RELEASE_COEF = 0.05; // Slower release (smooth decay)
    
    // Dynamic Range Config
    const DECAY_RATE = 0.992; // Slightly faster decay for responsiveness
    const MIN_MAX_VOLUME = 0.03; // Noise floor
    const GAMMA = 0.6; // More aggressive curve for better low-level visibility
    const BOOST_FACTOR = 1.4; // Stronger visual presence
    const MIN_DISPLAY = 0.15; // Minimum visual activity when recording

    // --- Visualization Config ---
    // Gradients
    let gradient;
    function createGradient() {
        // Create gradient relative to expected max width (~100px)
        gradient = ctx.createLinearGradient(0, 0, 100, 0);
        gradient.addColorStop(0, '#4facfe');    // Light Blue
        gradient.addColorStop(0.5, '#00f2fe');  // Cyan
        gradient.addColorStop(1, '#ff4757');    // Red/Pink Accent
    }
    createGradient();

    // --- Controls ---
    function showRecordingUI() {
        if (isRecording) return;
        isRecording = true;

        // Show UI
        overlay.classList.add('visible');

        // Start Waveform
        startWaveform();
    }

    function hideRecordingUI() {
        if (!isRecording) return;
        isRecording = false;

        // Hide UI
        overlay.classList.remove('visible');

        // Stop Waveform
        stopWaveform();
    }

    // --- Waveform Animation (DEMO / SIMULATION) ---
    function startWaveform() {
        if (animationId) cancelAnimationFrame(animationId);

        let phase = 0;
        // Reduced amplitude for compact height (48px height -> center is 24px)
        const amplitudeBase = 8;

        function draw() {
            if (!isRecording) return;

            // Clear
            ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr);

            const width = canvas.width / dpr;
            const height = canvas.height / dpr;
            const centerY = height / 2;

            ctx.lineWidth = 2.5;
            ctx.strokeStyle = gradient;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            // Line 1: Main Wave
            ctx.beginPath();
            phase += 0.15; // Speed

            // Smoothly interpolate currentLevel towards targetLevel
            currentLevel += (targetLevel - currentLevel) * 0.1;

            // Ensure a minimum visibility even when silent (optional)
            const displayVolume = Math.max(currentLevel, 0.1);

            for (let x = 0; x <= width; x += 2) {
                // Use the smoothed audio level
                const volume = displayVolume;

                // Adjusted frequencies for smaller width
                const y1 = Math.sin(x * 0.05 + phase);
                const y2 = Math.sin(x * 0.1 - phase * 0.5);
                const noise = y1 * y2;

                const carrier = Math.sin(x * 0.15 + phase * 2);

                const y = centerY + (carrier * noise * amplitudeBase * volume);

                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();

            // Line 2: Ghost Wave (Subtle)
            ctx.beginPath();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.lineWidth = 1.5;
            for (let x = 0; x <= width; x += 4) {
                const y = centerY + Math.sin(x * 0.08 + phase + 1) * (amplitudeBase * 0.6 * displayVolume);
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();

            animationId = requestAnimationFrame(draw);
        }

        draw();
    }

    function stopWaveform() {
        cancelAnimationFrame(animationId);
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear all
    }

    // Expose for Python
    window.showRecordingUI = showRecordingUI;
    window.hideRecordingUI = hideRecordingUI;
    window.updateWaveform = (level) => {
        // 1. Envelope Follower (smooth the raw input)
        // Attack fast, release slow for natural feel
        if (level > smoothedLevel) {
            smoothedLevel += (level - smoothedLevel) * ATTACK_COEF;
        } else {
            smoothedLevel += (level - smoothedLevel) * RELEASE_COEF;
        }
        
        // 2. Track recent peaks for percentile-based normalization
        recentPeaks.push(smoothedLevel);
        if (recentPeaks.length > MAX_PEAKS_HISTORY) {
            recentPeaks.shift();
        }
        
        // 3. Calculate dynamic max from recent peaks (use 90th percentile)
        const sortedPeaks = [...recentPeaks].sort((a, b) => b - a);
        const percentileIdx = Math.floor(sortedPeaks.length * 0.1);
        const recentMax = sortedPeaks[percentileIdx] || smoothedLevel;
        
        // 4. Adaptive Peak Tracking with decay
        maxVolume *= DECAY_RATE;
        const candidateMax = Math.max(recentMax, smoothedLevel);
        if (candidateMax > maxVolume) {
            maxVolume = candidateMax;
        }

        // Prevent division by tiny numbers (noise floor protection)
        const effectiveMax = Math.max(maxVolume, MIN_MAX_VOLUME);

        // 5. Normalize (0.0 to 1.0 range)
        let normalized = smoothedLevel / effectiveMax;
        normalized = Math.min(normalized, 1.0); // Clamp

        // 6. Non-linear mapping for better visual dynamics
        // S-curve approximation: boosts mid-range, compresses extremes
        let visualLevel;
        if (normalized < 0.5) {
            // Boost lower half with power curve
            visualLevel = Math.pow(normalized * 2, GAMMA) * 0.5;
        } else {
            // Softer compression for upper half
            visualLevel = 0.5 + (normalized - 0.5) * 0.8;
        }

        // 7. Apply boost and ensure minimum visibility
        visualLevel = visualLevel * BOOST_FACTOR;
        visualLevel = Math.max(visualLevel, MIN_DISPLAY);

        // 8. Set target with cap
        targetLevel = Math.min(visualLevel, 1.5); 
    };
});
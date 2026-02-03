from model import process_claim, clear_all
from datetime import datetime
import gradio as gr
import os
from dotenv import load_dotenv
load_dotenv()

# Custom CSS for insurance theme
custom_css = """
.insurance-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
}
.insurance-logo {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
}
.model-info {
    background: #f0f8ff;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #2a5298;
    margin: 10px 0;
}
.download-btn {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}
.download-btn:hover {
    background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
}
"""

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as app:
    # Header
    gr.HTML("""
    <div class="insurance-header">
        <div class="insurance-logo">🏥 AI Insurance Claim Assistant</div>
        <p>Upload claim photos and get instant AI-powered damage assessment</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            # Image upload
            image_input = gr.Image(
                label="📸 Upload Claim Photo",
                type="filepath",
                height=300
            )
            
            # User description
            description_input = gr.Textbox(
                label="📝 Claim Description",
                placeholder="Describe the incident: e.g., 'Car accident front collision', 'Water damage in kitchen', 'Theft damage to front door'...",
                lines=4
            )
            
            # Model selection
            model_choice = gr.Radio(
                label="🤖 Select AI Model",
                choices=[
                    "BLIP (Free - Fast)",
                    "GPT-4 Vision (Paid - More Accurate)"
                ],
                value="BLIP (Free - Fast)",
                info="GPT-4 provides more detailed analysis but requires OpenAI API key"
            )
            
            # API key input (optional)
            with gr.Accordion("🔑 OpenAI API Configuration (for GPT-4)", open=False):
                api_key_input = gr.Textbox(
                    label="OpenAI API Key",
                    type="password",
                    placeholder="sk-... (leave empty if using BLIP)",
                    info="Required only for GPT-4 Vision"
                )
                
                def set_api_key(key):
                    if key:
                        os.environ["OPENAI_API_KEY"] = key
                        return "✅ API key set successfully"
                    return "ℹ️ No API key provided"
                
                api_key_btn = gr.Button("Set API Key")
                api_key_status = gr.Textbox(label="Status", interactive=False)
                api_key_btn.click(set_api_key, inputs=api_key_input, outputs=api_key_status)
            
            # Action buttons
            with gr.Row():
                analyze_btn = gr.Button("🔍 Analyze Damage", variant="primary", scale=2)
                clear_btn = gr.Button("🗑️ Clear All", variant="secondary", scale=1)
    
        with gr.Column(scale=2):
            # Results
            results_output = gr.Markdown(
                label="📊 Damage Assessment",
                value="*Analysis results will appear here...*"
            )
            
            # Save status
            save_status = gr.Textbox(
                label="💾 Record Status",
                interactive=False
            )
            
            # Download section
            with gr.Accordion("📥 Download Report", open=False):
                gr.Markdown("""
                The claim record has been automatically saved. You can:
                1. Find it in the `claim_records/` folder
                2. Copy the analysis text above
                3. Export as text file below
                """)
                
                def create_report_text(image, description, analysis):
                    report = f"""
                    INSURANCE CLAIM REPORT
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    
                    CLAIM DESCRIPTION:
                    {description}
                    
                    VISUAL DAMAGE ASSESSMENT:
                    {analysis}
                    
                    --- END OF REPORT ---
                    """
                    return report
                
                report_text = gr.Textbox(
                    label="Report Text",
                    interactive=True,
                    lines=10
                )
                
                # Update report text when analysis is done
                def update_report(image, description, analysis):
                    return create_report_text(image, description, analysis)
                
                # File download
                report_download = gr.File(label="Download Report")
    
    # Examples
    with gr.Accordion("📋 Example Claims", open=False):
        gr.Examples(
            examples=[
                ["examples/car_accident.jpg", "Front collision with another vehicle at intersection"],
                ["examples/water_damage.jpg", "Kitchen flooded due to pipe burst"],
                ["examples/fire_damage.jpg", "Electrical fire in living room"]
            ],
            inputs=[image_input, description_input],
            label="Try these examples (need example images in 'examples/' folder)"
        )
    
    # Model info
    gr.HTML("""
    <div class="model-info">
        <strong>Model Information:</strong><br>
        <strong>BLIP (Free):</strong> Fast, offline model. Good for basic damage recognition.<br>
        <strong>GPT-4 Vision (Paid):</strong> More detailed analysis. Understands context better. Requires OpenAI API key.
    </div>
    """)
    
    # Footer
    gr.HTML("""
    <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
        <p>⚠️ This AI tool assists with preliminary damage assessment. All claims must be verified by a licensed insurance adjuster.</p>
        <p>🔒 Your data is processed locally (BLIP) or via secure API (GPT-4). No data is stored permanently.</p>
    </div>
    """)
    
    # Connect buttons
    analyze_btn.click(
        process_claim,
        inputs=[image_input, description_input, model_choice],
        outputs=[results_output, save_status]
    ).then(
        update_report,
        inputs=[image_input, description_input, results_output],
        outputs=[report_text]
    )
    
    clear_btn.click(
        clear_all,
        outputs=[image_input, description_input, results_output, save_status]
    )

# ==================== RUN THE APP ====================

# Create example directory for demo
os.makedirs("examples", exist_ok=True)
os.makedirs("claim_records", exist_ok=True)

# Launch instructions
print("✨ Insurance Claim Assistant is ready!")
print("\nTo launch the app, run:")
print("1. For local testing: app.launch(share=False)")
print("2. For public link: app.launch(share=True)")
print("\nFor GPT-4 Vision, set your OpenAI API key in the app configuration.")

# Uncomment to launch directly
# app.launch(share=True)  # Set share=False for local only
app.launch(
    # share=True,  # Creates public link
    server_name="0.0.0.0",
    server_port=7860
)
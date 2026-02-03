import os
from PIL import Image
import torch
import base64
from datetime import datetime

# Optionally for GPT-4
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False

# Initialize models dictionary
models = {}

# ==================== FREE MODELS ====================

def load_blip_model():
    """Load BLIP model for free captioning"""
    from transformers import BlipProcessor, BlipForConditionalGeneration
    
    print("Loading BLIP model...")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    
    # Move to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    
    return processor, model, device

def caption_with_blip(image, user_description):
    """Generate caption using BLIP model with insurance context"""
    if 'blip' not in models:
        models['blip'] = load_blip_model()
    
    processor, model, device = models['blip']
    
    # Prepare prompt with insurance context
    prompt = f"Insurance claim photo showing {user_description}. Detailed description:"
    
    try:
        # Convert Gradio image to PIL
        if isinstance(image, str):
            pil_image = Image.open(image).convert('RGB')
        else:
            pil_image = Image.fromarray(image).convert('RGB')
        
        # Process image
        inputs = processor(pil_image, prompt, return_tensors="pt").to(device)
        
        # Generate caption
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=100,
                num_beams=5,
                temperature=0.7,
                do_sample=True
            )
        
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        
        # Format for insurance context
        formatted_caption = format_insurance_caption(caption, user_description)
        return formatted_caption
        
    except Exception as e:
        return f"Error with BLIP model: {str(e)}"

# ==================== GPT-4 VISION ====================

def setup_openai_client():
    """Setup OpenAI client with API key"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Try to get from Gradio secrets or user input
        return None
    
    return OpenAI(api_key=api_key)

def caption_with_gpt4(image, user_description):
    """Generate caption using GPT-4 Vision"""
    if not OPENAI_AVAILABLE:
        return "OpenAI library not installed. Please install with: pip install openai"
    
    client = setup_openai_client()
    if not client:
        return "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
    
    try:
        # Convert image to base64
        if isinstance(image, str):
            with open(image, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            mime_type = "image/jpeg"
        else:
            from io import BytesIO
            buffered = BytesIO()
            Image.fromarray(image).save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            mime_type = "image/jpeg"
        
        # Create system message for insurance context
        system_prompt = """You are an insurance claim analyst. Describe the damage in the image with:
        1. Type of damage (collision, fire, water, vandalism, etc.)
        2. Severity level (minor, moderate, severe)
        3. Visible components affected
        4. Estimated repair complexity
        5. Any safety concerns
        
        Be factual, detailed, and objective."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Claim description from client: '{user_description}'\n\nAnalyze this insurance claim photo and provide a detailed damage assessment:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.2  # Lower temperature for more factual responses
        )
        
        caption = response.choices[0].message.content
        return format_insurance_caption(caption, user_description)
        
    except Exception as e:
        return f"Error with GPT-4 Vision: {str(e)}"

# ==================== HELPER FUNCTIONS ====================

def format_insurance_caption(caption, user_description):
    """Format the caption for insurance context"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    formatted = f"""🚑 **INSURANCE CLAIM ANALYSIS** 🚑

**📋 Claim Description:** {user_description}

**📊 AI Damage Assessment:**
{caption}

**📅 Analysis Date:** {current_time}
**⚡ Assessment Method:** AI-Powered Visual Analysis

---
*This is an AI-assisted analysis. Please verify with a human adjuster.*
"""
    return formatted

def save_claim_record(image, user_description, ai_caption, model_used):
    """Save claim record to file (simplified version)"""
    try:
        # Create records directory
        os.makedirs("claim_records", exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"claim_records/claim_{timestamp}.txt"
        
        # Save record
        record = {
            "timestamp": timestamp,
            "user_description": user_description,
            "ai_caption": ai_caption,
            "model_used": model_used,
            "filename": filename
        }
        
        with open(filename, "w") as f:
            f.write(f"INSURANCE CLAIM RECORD\n")
            f.write(f"="*50 + "\n")
            f.write(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model Used: {model_used}\n\n")
            f.write(f"USER DESCRIPTION:\n{user_description}\n\n")
            f.write(f"AI ANALYSIS:\n{ai_caption}\n")
            f.write(f"="*50 + "\n")
        
        # Save image if provided
        if image:
            if isinstance(image, str):
                import shutil
                img_filename = f"claim_records/claim_{timestamp}.jpg"
                shutil.copy(image, img_filename)
            else:
                img_filename = f"claim_records/claim_{timestamp}.jpg"
                Image.fromarray(image).save(img_filename)
        
        return f"✅ Record saved: {filename}"
    except Exception as e:
        return f"⚠️ Could not save record: {str(e)}"

# ==================== GRADIO INTERFACE ====================

def process_claim(image, user_description, model_choice):
    """Main processing function for Gradio"""
    if image is None:
        return "⚠️ Please upload an image first.", ""
    
    if not user_description.strip():
        return "⚠️ Please provide a description of the incident.", ""
    
    # Show processing status
    yield "⏳ Analyzing image... Please wait.", ""
    
    # Choose model based on selection
    if model_choice == "GPT-4 Vision (Paid - More Accurate)":
        if not OPENAI_AVAILABLE:
            result = "❌ OpenAI not configured. Please install with 'pip install openai' and set API key."
        else:
            result = caption_with_gpt4(image, user_description)
    else:  # Free model
        result = caption_with_blip(image, user_description)
    
    # Save the record
    save_status = save_claim_record(image, user_description, result, model_choice)
    
    yield result, save_status

def clear_all():
    """Clear all inputs"""
    return None, "", "", ""


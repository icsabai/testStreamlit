def get_ai_response(question, selected_area=None, image=None):
    if image is None:
        return "Please upload an image first."
    
    # Convert image to bytes for API request
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or 'PNG')
    img_bytes = img_byte_arr.getvalue()
    
    # Prepare API request
    files = {'image': img_bytes}
    data = {
        'question': question,
        'selection': selected_area if selected_area else None
    }
    
    # Send request to AI service
    response = requests.post('your-ai-service-url', files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        
        # Handle different response types
        if result.get('chart_data'):
            # Process chart data
            st.session_state.chart_data = pd.DataFrame(result['chart_data'])
        
        if result.get('annotation'):
            # Process annotation
            annotate_image(result['annotation']['area'], result['annotation']['label'])
        
        return result.get('text_response', 'Analysis complete.')
    else:
        return "Sorry, I encountered an error analyzing the image."

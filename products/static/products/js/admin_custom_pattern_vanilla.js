document.addEventListener('DOMContentLoaded', function() {
    console.log('Custom pattern admin script loaded (vanilla JS)');
    
    // Find the pattern field and custom pattern field
    var patternField = document.getElementById('id_pattern');
    var customPatternField = document.getElementById('id_custom_pattern');
    var form = patternField ? patternField.closest('form') : null;
    
    console.log('Pattern field:', patternField);
    console.log('Custom pattern field:', customPatternField);
    console.log('Form:', form);
    
    function toggleCustomPatternField() {
        var selectedPattern = patternField ? patternField.value : '';
        console.log('Selected pattern:', selectedPattern);
        
        if (selectedPattern === 'custom') {
            customPatternField.disabled = false;
            customPatternField.required = true;
            
            // Add visual styling
            var fieldContainer = customPatternField.closest('.field-custom_pattern');
            if (fieldContainer) {
                var label = fieldContainer.querySelector('label');
                if (label && !label.classList.contains('required')) {
                    label.classList.add('required');
                }
                fieldContainer.classList.add('required-field');
            }
            console.log('Custom pattern field enabled and required');
        } else {
            customPatternField.disabled = true;
            customPatternField.required = false;
            customPatternField.value = ''; // Clear the field when disabled
            
            // Remove visual styling
            var fieldContainer = customPatternField.closest('.field-custom_pattern');
            if (fieldContainer) {
                var label = fieldContainer.querySelector('label');
                if (label) {
                    label.classList.remove('required');
                }
                fieldContainer.classList.remove('required-field');
            }
            console.log('Custom pattern field disabled and cleared');
        }
    }
    
    function validateCustomPattern() {
        var selectedPattern = patternField ? patternField.value : '';
        if (selectedPattern === 'custom' && customPatternField && !customPatternField.value.trim()) {
            alert('Custom pattern name is required when "Custom Pattern" is selected.');
            customPatternField.focus();
            return false;
        }
        return true;
    }
    
    if (patternField && customPatternField && form) {
        // Initial state
        toggleCustomPatternField();
        
        // Change event handler
        patternField.addEventListener('change', toggleCustomPatternField);
        
        // Form submission validation
        form.addEventListener('submit', function(e) {
            if (!validateCustomPattern()) {
                e.preventDefault();
                return false;
            }
        });
        
        // Also handle when page loads with existing values
        setTimeout(toggleCustomPatternField, 100);
    } else {
        console.error('Required fields or form not found');
    }
});

(function($) {
    'use strict';
    
    $(document).ready(function() {
        console.log('Custom pattern admin script loaded');
        
        // Find the pattern field and custom pattern field
        var patternField = $('#id_pattern');
        var customPatternField = $('#id_custom_pattern');
        
        console.log('Pattern field:', patternField.length);
        console.log('Custom pattern field:', customPatternField.length);
        
        function toggleCustomPatternField() {
            var selectedPattern = patternField.val();
            console.log('Selected pattern:', selectedPattern);
            
            if (selectedPattern === 'custom') {
                customPatternField.prop('disabled', false);
                customPatternField.prop('required', true);
                customPatternField.closest('.form-row, .field-box, .field-custom_pattern').find('label').addClass('required');
                console.log('Custom pattern field enabled and required');
            } else {
                customPatternField.prop('disabled', true);
                customPatternField.prop('required', false);
                customPatternField.closest('.form-row, .field-box, .field-custom_pattern').find('label').removeClass('required');
                customPatternField.val(''); // Clear the field when disabled
                console.log('Custom pattern field disabled and cleared');
            }
        }
        
        // Initial state
        toggleCustomPatternField();
        
        // Change event handler
        patternField.on('change', toggleCustomPatternField);
        
        // Also handle when page loads with existing values
        setTimeout(toggleCustomPatternField, 100);
    });
})(django.jQuery || jQuery);

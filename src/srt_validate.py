"""
Compact SRT validator and fixer for editor support.
"""

import os
import re

def fix_timestamp(timestamp_str):
    """Fix a single timestamp to HH:MM:SS,mmm format."""
    if not timestamp_str:
        return timestamp_str
    
    # Remove any whitespace
    timestamp_str = timestamp_str.strip()
    
    # Replace dots with commas for milliseconds
    timestamp_str = timestamp_str.replace('.', ',')
    
    # Split by colon and comma to get components
    parts = timestamp_str.replace(',', ':').split(':')
    
    if len(parts) == 2:
        # MM:SSS format (minutes:milliseconds)
        return f"00:00:{parts[0].zfill(2)},{parts[1].zfill(3)}"
    elif len(parts) == 3:
        # MM:SS:mmm or HH:MM:SS format
        if len(parts[2]) == 3:  # milliseconds
            return f"00:{parts[0].zfill(2)}:{parts[1].zfill(2)},{parts[2].zfill(3)}"
        else:  # seconds
            return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:{parts[2].zfill(2)},000"
    elif len(parts) == 4:
        # HH:MM:SS:mmm or H:MM:SS:mmm
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:{parts[2].zfill(2)},{parts[3].zfill(3)}"
    
    # If format is already correct or unrecognizable, return as is
    return timestamp_str

def fix_common_srt_issues(content):
    """Fix common SRT formatting issues."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        line = line.strip()
        
        if ' --> ' in line:
            # Split timestamp line and fix each timestamp
            parts = line.split(' --> ')
            if len(parts) == 2:
                start_time = fix_timestamp(parts[0])
                end_time = fix_timestamp(parts[1])
                fixed_lines.append(f"{start_time} --> {end_time}")
            else:
                # Malformed arrow, keep as is
                fixed_lines.append(line)
        elif line.isdigit():
            # Subtitle index line
            fixed_lines.append(line)
        elif line:
            # Text line - check for length and break if needed
            # Remove markdown formatting first
            line = re.sub(r'\*\*(.*?)\*\*|\*(.*?)\*|__(.*?)__|_(.*?)_', r'\1\2\3\4', line)
            
            # Check if line exceeds limits (60 characters or 10 words)
            words = line.split()
            if len(line) > 60 or len(words) > 10:
                # Break the line into smaller chunks
                broken_lines = break_long_line(line)
                fixed_lines.extend(broken_lines)
            else:
                fixed_lines.append(line)
        else:
            # Empty line
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def break_long_line(text, max_chars=60, max_words=10):
    """Break a long text line into multiple lines based on character and word limits."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        # Check if adding this word would exceed limits
        word_length = len(word)
        new_length = current_length + word_length + (1 if current_line else 0)  # +1 for space
        
        if (len(current_line) >= max_words or 
            new_length > max_chars) and current_line:
            # Current line is full, start a new one
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length
        else:
            # Add word to current line
            current_line.append(word)
            current_length = new_length
    
    # Add the last line if it has content
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def validate_srt_format(content):
    """Quick SRT validation with line length checking."""
    lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
    
    if not lines:
        return {'is_valid': False, 'errors': ['Empty file']}
    
    errors = []
    timestamp_pattern = r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$'
    
    i = 0
    subtitle_count = 0
    
    while i < len(lines):
        subtitle_count += 1
        
        # Check index (should be number)
        if not lines[i].isdigit():
            errors.append(f"Subtitle {subtitle_count}: Invalid index format")
        i += 1
        
        # Check timestamp
        if i < len(lines) and not re.match(timestamp_pattern, lines[i]):
            errors.append(f"Subtitle {subtitle_count}: Invalid timestamp format")
        i += 1
        
        # Check text lines for length limits
        text_line_count = 0
        while i < len(lines) and not lines[i].isdigit():
            text_line = lines[i]
            text_line_count += 1
            
            # C
            # heck character and word limits
            words = text_line.split()
            if len(text_line) > 60:
                errors.append(f"Subtitle {subtitle_count}, line {text_line_count}: Text too long ({len(text_line)} chars, max 60)")
            if len(words) > 10:
                errors.append(f"Subtitle {subtitle_count}, line {text_line_count}: Too many words ({len(words)} words, max 10)")
            
            i += 1
    
    return {'is_valid': len(errors) == 0, 'errors': errors, 'subtitle_count': subtitle_count}

def validate_and_fix_srt(srt_path, auto_fix=True, backup_original=True):
    """Main function: validate and fix SRT file."""
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation = validate_srt_format(content)
        
        if validation['is_valid']:
            return {'path': srt_path, 'was_fixed': False, 'validation_result': validation}
        
        if not auto_fix:
            return {'path': srt_path, 'was_fixed': False, 'validation_result': validation}
        
        # Create backup
        if backup_original:
            backup_path = os.path.join(os.path.dirname(srt_path), 'backup', os.path.basename(srt_path))
            backup_path = backup_path.replace('.srt', '_backup.srt')
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)

            print(f"Creating backup at {backup_path}")
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Fix and save
        fixed_content = fix_common_srt_issues(content)
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        fixed_validation = validate_srt_format(fixed_content)
        return {'path': srt_path, 'was_fixed': True, 'validation_result': fixed_validation}
        
    except Exception as e:
        return {
            'path': srt_path, 
            'was_fixed': False, 
            'validation_result': {'is_valid': False, 'errors': [str(e)]}
        }

def print_validation_results(validation_result):
    """Print validation results."""
    if validation_result['is_valid']:
        subtitle_count = validation_result.get('subtitle_count', 0)
        print(f"    ✅ SRT file is valid ({subtitle_count} subtitles)")
    else:
        print(f"    ❌ SRT validation failed: {len(validation_result['errors'])} errors")
        for error in validation_result['errors'][:5]:  # Show first 5 errors
            print(f"       - {error}")
        if len(validation_result['errors']) > 5:
            print(f"       ... and {len(validation_result['errors']) - 5} more errors")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python srt_validate.py <path_to_srt_file>")
        sys.exit(1)
    
    srt_path = sys.argv[1]
    result = validate_and_fix_srt(srt_path)
    
    print(f"Validation result for '{srt_path}':")
    print_validation_results(result['validation_result'])
    
    if result['was_fixed']:
        print(f"    ✅ SRT file was fixed and saved at: {srt_path}")
    else:
        print(f"    ❌ SRT file was not fixed, original content remains unchanged.")
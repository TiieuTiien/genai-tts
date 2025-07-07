"""
Compact SRT validator and fixer for editor support.
"""

import re

def fix_common_srt_issues(content):
    """Fix common SRT formatting issues."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        line = line.strip()
        
        if ' --> ' in line:
            # Fix timestamp formats
            # MM:mmm -> 00:MM:SS,mmm
            line = re.sub(r'^(\d{2}):(\d{3}) --> (\d{2}):(\d{3})$', r'00:00:\1,\2 --> 00:00:\3,\4', line)
            # MM:SS.mmm -> 00:MM:SS,mmm
            line = re.sub(r'^(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2})\.(\d{3})$', r'00:\1:\2,\3 --> 00:\4:\5,\6', line)
            # MM:SS:mmm -> 00:MM:SS,mmm
            line = re.sub(r'^(\d{2}):(\d{2}):(\d{3}) --> (\d{2}):(\d{2}):(\d{3})$', r'00:\1:\2,\3 --> 00:\4:\5,\6', line)
            # H:MM:SS,mmm -> 0H:MM:SS,mmm
            line = re.sub(r'^(\d):(\d{2}):(\d{2}),(\d{3}) --> (\d):(\d{2}):(\d{2}),(\d{3})$', r'0\1:\2:\3,\4 --> 0\5:\6:\7,\8', line)
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
            backup_path = srt_path.replace('.srt', '_backup.srt')
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
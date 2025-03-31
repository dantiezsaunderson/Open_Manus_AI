"""
Coding Support Module

This module provides coding assistance, code generation, and code analysis
capabilities for the Open Manus AI system.
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class CodingSupportModule:
    """
    Coding Support Module for providing programming assistance.
    """
    
    def __init__(self, ai_engine):
        """
        Initialize the Coding Support Module.
        
        Args:
            ai_engine (AIEngine): The AI engine instance
        """
        self.ai_engine = ai_engine
        logger.info("Coding Support Module initialized")
    
    def generate_code(self, prompt, language="python", detailed=True):
        """
        Generate code based on a natural language prompt.
        
        Args:
            prompt (str): Natural language description of the code to generate
            language (str, optional): Programming language to generate code in
            detailed (bool, optional): Whether to include detailed comments
            
        Returns:
            dict: Generated code and explanation
        """
        try:
            # Create system message based on requirements
            system_message = f"You are an expert {language} programmer. "
            system_message += "Generate clean, efficient, and well-structured code based on the user's requirements. "
            
            if detailed:
                system_message += "Include detailed comments explaining the code and implementation decisions. "
                system_message += "Structure your response with: 1) A brief explanation of the approach, "
                system_message += "2) The complete code implementation, and 3) Usage examples if applicable."
            else:
                system_message += "Focus on generating just the code with minimal necessary comments."
            
            # Enhance the prompt for better results
            enhanced_prompt = f"Please write {language} code that accomplishes the following:\n\n{prompt}\n\n"
            enhanced_prompt += f"Provide the complete implementation in {language}."
            
            # Generate response
            response = self.ai_engine.generate_response(enhanced_prompt, system_message=system_message)
            
            # Extract code from response
            code = self._extract_code_from_response(response, language)
            
            return {
                "code": code,
                "explanation": response,
                "language": language,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {
                "code": "",
                "explanation": f"Error generating code: {str(e)}",
                "language": language,
                "success": False
            }
    
    def _extract_code_from_response(self, response, language):
        """
        Extract code blocks from an AI response.
        
        Args:
            response (str): The AI's response text
            language (str): The programming language
            
        Returns:
            str: Extracted code or empty string if no code found
        """
        import re
        
        # Look for code blocks with language tag
        pattern = f"```{language}(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no language-specific blocks found, try generic code blocks
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks found, try to extract based on indentation
        lines = response.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                in_code_block = True
                code_lines.append(line)
            elif in_code_block:
                if line.strip() == '' and len(code_lines) > 0:
                    # Empty line might end a code block, but only if we have a non-empty block following
                    continue
                elif line.startswith('    ') or line.startswith('\t') or line.strip() == '':
                    code_lines.append(line)
                else:
                    in_code_block = False
        
        if code_lines:
            return '\n'.join(code_lines)
        
        # If all else fails, return empty string
        return ""
    
    def analyze_code(self, code, language="python"):
        """
        Analyze code for quality, bugs, and improvement suggestions.
        
        Args:
            code (str): Code to analyze
            language (str, optional): Programming language of the code
            
        Returns:
            dict: Analysis results
        """
        try:
            result = self.ai_engine.analyze_code(code, language)
            return result
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {
                "analysis": f"Error analyzing code: {str(e)}",
                "success": False
            }
    
    def execute_code(self, code, language="python", timeout=30):
        """
        Safely execute code in a sandbox environment.
        
        Args:
            code (str): Code to execute
            language (str, optional): Programming language of the code
            timeout (int, optional): Maximum execution time in seconds
            
        Returns:
            dict: Execution results
        """
        try:
            if language.lower() != "python":
                return {
                    "output": f"Execution of {language} code is not supported yet.",
                    "error": "Unsupported language",
                    "success": False
                }
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(code.encode('utf-8'))
            
            # Execute the code in a subprocess with timeout
            try:
                result = subprocess.run(
                    ['python', temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return {
                    "output": result.stdout,
                    "error": result.stderr,
                    "success": result.returncode == 0
                }
            except subprocess.TimeoutExpired:
                return {
                    "output": "",
                    "error": f"Execution timed out after {timeout} seconds",
                    "success": False
                }
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return {
                "output": "",
                "error": f"Error executing code: {str(e)}",
                "success": False
            }
    
    def complete_code(self, partial_code, language="python"):
        """
        Complete partial code snippets.
        
        Args:
            partial_code (str): Incomplete code snippet
            language (str, optional): Programming language of the code
            
        Returns:
            dict: Completed code
        """
        try:
            system_message = f"You are an expert {language} programmer. Complete the following code snippet. Only provide the complete code without explanations."
            
            prompt = f"Complete this {language} code:\n\n{partial_code}\n\nProvide the full, completed code:"
            
            response = self.ai_engine.generate_response(prompt, system_message=system_message)
            
            # Extract code from response
            completed_code = self._extract_code_from_response(response, language)
            
            # If no code block was found, use the entire response
            if not completed_code:
                completed_code = response
            
            return {
                "completed_code": completed_code,
                "language": language,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error completing code: {e}")
            return {
                "completed_code": partial_code,
                "language": language,
                "error": str(e),
                "success": False
            }

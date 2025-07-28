    def _generate_conversational_response(self) -> None:
        """Generate a conversational response without tool calling prompts."""
        try:
            # Build conversational prompt without tool examples
            conversation_history = self.context_manager.get_conversation_history()
            
            # Create a simple conversational system prompt
            conversational_system = f"""You are a helpful AI coding assistant called DeepCoderX. You are friendly, knowledgeable, and ready to help with coding tasks.

Key facts about you:
- You can help with programming, debugging, code analysis, and development tasks
- You have access to file system tools when needed for coding work
- You are running locally using a GGUF model with direct inference
- You can work with multiple programming languages and frameworks

Respond naturally and conversationally. Be helpful and engaging."""
            
            # Format conversation history for chat template
            formatted_history = self._format_conversation_history(conversation_history)
            
            # Use chat template formatting for conversational response
            prompt = self.chat_formatter.format_prompt(
                system_prompt=conversational_system,
                user_prompt=self.ctx.user_input,
                conversation_history=formatted_history
            )
            
            if self.debug_mode:
                console.print(f"[cyan]Generating conversational response with {len(formatted_history)} history messages[/]")
                console.print(f"[dim]Conversational prompt length: {len(prompt)} characters[/]")
            
            # Generate response with conversational settings
            self.ctx.status_message = f"Chatting with {self.provider_config['name']}..."
            response = self._generate_conversational_gguf_response(prompt)
            
            if response:
                self.ctx.response = response
                self.context_manager.add_assistant_message(response)
                
                if self.debug_mode:
                    console.print(f"[green]Generated conversational response: {response[:100]}...[/]")
            else:
                self.ctx.response = "[yellow]I'm here and ready to help! What would you like to work on?[/]"
                
        except Exception as e:
            self.ctx.response = f"[red]Conversational Error:[/] {str(e)}"
            if self.debug_mode:
                console.print(f"[bold red]Conversational Error:[/] {e}")
    
    def _generate_conversational_gguf_response(self, prompt: str) -> str:
        """Generate response using GGUF model with conversational settings."""
        try:
            start_time = time.time()
            
            # Use more creative settings for conversational responses
            temperature = 0.7  # More creative than tool calling
            max_tokens = self.provider_config.get("max_tokens", 512)  # Shorter for conversation
            
            # Generate completion with conversational stop sequences
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                top_k=50,
                repeat_penalty=1.1,
                stop=[
                    "Human:", "User:", "<|start_header_id|>user<|end_header_id|>",
                    "\\n\\nUser:", "\\n\\nHuman:", "<|eot_id|>",
                    "<tool_call>", "</tool_call>"  # Prevent accidental tool calls
                ],
                echo=False
            )
            
            end_time = time.time()
            
            # Extract the generated text
            if isinstance(response, dict) and "choices" in response:
                generated_text = response["choices"][0]["text"]
            else:
                generated_text = str(response)
            
            # Log performance metrics
            if self.debug_mode:
                duration = end_time - start_time
                console.print(f"[dim]Conversational GGUF generation took {duration:.2f}s[/]")
            
            # Clean up the response
            cleaned_text = generated_text.strip()
            
            # Remove any accidental tool call remnants
            if "<tool_call>" in cleaned_text or "</tool_call>" in cleaned_text:
                # Extract text before any tool calls
                if "<tool_call>" in cleaned_text:
                    cleaned_text = cleaned_text.split("<tool_call>")[0].strip()
            
            return cleaned_text
            
        except Exception as e:
            console.print(f"[red]Conversational GGUF generation error: {e}[/]")
            raise

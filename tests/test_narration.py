import pytest
from app.services.narration import parse_chapter_to_script_blocks, DialogueBlock, NarrationBlock

class TestDeterministicScriptParser:
    def test_parses_pure_narration(self):
        text = "The wind howled through the empty streets."
        blocks = parse_chapter_to_script_blocks(text)
        assert len(blocks) == 1
        assert isinstance(blocks[0], NarrationBlock)
        assert blocks[0].text == "The wind howled through the empty streets."

    def test_parses_simple_dialogue(self):
        text = "Zorian sighed. \"This is ridiculous.\""
        blocks = parse_chapter_to_script_blocks(text)
        assert len(blocks) == 2
        assert isinstance(blocks[0], NarrationBlock)
        assert blocks[0].text == "Zorian sighed."
        assert isinstance(blocks[1], DialogueBlock)
        assert blocks[1].text == "This is ridiculous."

    def test_parses_dialogue_with_internal_punctuation(self):
        text = "\"Wait!\" she cried. \"Don't go.\""
        blocks = parse_chapter_to_script_blocks(text)
        assert len(blocks) == 3
        assert isinstance(blocks[0], DialogueBlock)
        assert blocks[0].text == "Wait!"
        assert isinstance(blocks[1], NarrationBlock)
        assert blocks[1].text == "she cried."
        assert isinstance(blocks[2], DialogueBlock)
        assert blocks[2].text == "Don't go."

    def test_strips_empty_blocks_and_whitespace(self):
        text = "   \n\n  \"Hello.\" \n  "
        blocks = parse_chapter_to_script_blocks(text)
        assert len(blocks) == 1
        assert isinstance(blocks[0], DialogueBlock)
        assert blocks[0].text == "Hello."

from unittest.mock import patch
from app.services.narration import resolve_dialogue_speakers

class TestResolveDialogueSpeakers:
    @patch('app.services.narration.analyze_text_json')
    def test_resolves_speakers_via_llm_batch(self, mock_analyze, monkeypatch):
        # Setup mock to return the expected JSON format
        mock_analyze.return_value = {
            "speakers": {
                "0": "Zorian",
                "1": "Ilsa"
            }
        }
        
        blocks = [
            NarrationBlock(text="Zorian sighed."),
            DialogueBlock(text="This is ridiculous."),
            NarrationBlock(text="Ilsa crossed her arms."),
            DialogueBlock(text="I agree.")
        ]
        
        resolved_blocks = resolve_dialogue_speakers(blocks)
        
        # Verify the dialogue blocks have their speaker assigned
        assert resolved_blocks[1].speaker == "Zorian"
        assert resolved_blocks[3].speaker == "Ilsa"
        
        # Verify the mock was called with a prompt containing the quotes
        assert mock_analyze.called
        prompt = mock_analyze.call_args[0][0]
        assert "This is ridiculous." in prompt
        assert "I agree." in prompt
        
    def test_handles_no_dialogue_blocks(self):
        blocks = [NarrationBlock(text="Just some narration.")]
        resolved_blocks = resolve_dialogue_speakers(blocks)
        assert len(resolved_blocks) == 1
        assert getattr(resolved_blocks[0], 'speaker', None) is None  # Narration shouldn't have a speaker field set to a name based on dialogue

    @patch('app.services.narration.analyze_text_json')
    def test_handles_missing_keys_in_llm_response(self, mock_analyze):
        # LLM misses index 1
        mock_analyze.return_value = {
            "speakers": {
                "0": "Zorian"
            }
        }
        blocks = [
            DialogueBlock(text="This is ridiculous."),
            DialogueBlock(text="I agree.")
        ]
        
        resolved_blocks = resolve_dialogue_speakers(blocks)
        
        assert resolved_blocks[0].speaker == "Zorian"
        assert resolved_blocks[1].speaker == "Narrator"  # Default fallback due to missing key

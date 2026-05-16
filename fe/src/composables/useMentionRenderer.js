import { ref, computed } from 'vue';

export function useMentionRenderer() {
  function renderContentWithMentions(content, characterMentions, onMentionClick) {
    if (!content || !characterMentions || characterMentions.length === 0) {
      return content;
    }

    let renderedContent = content;

    // Sort mentions by mention_text length (longest first) to avoid partial replacements
    const sortedMentions = [...characterMentions].sort(
      (a, b) => b.mention_text.length - a.mention_text.length
    );

    for (const mention of sortedMentions) {
      const mentionText = mention.mention_text;
      const character = mention.character;

      if (!character) continue;

      // Create a unique placeholder for this mention
      const placeholder = `__MENTION_${mention.id}__`;

      // Replace the mention text with the placeholder
      renderedContent = renderedContent.replace(
        new RegExp(escapeRegExp(mentionText), 'g'),
        placeholder
      );
    }

    // Now replace all placeholders with clickable links
    for (const mention of sortedMentions) {
      const placeholder = `__MENTION_${mention.id}__`;
      const character = mention.character;

      if (!character) continue;

      const mentionLink = `<span class="character-mention" data-character-id="${character.id}">@${character.name}</span>`;

      renderedContent = renderedContent.replace(placeholder, mentionLink);
    }

    return renderedContent;
  }

  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  return {
    renderContentWithMentions
  };
}

/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { Node, mergeAttributes } from "@tiptap/core";
import type { MarkdownSerializerState } from "@tiptap/pm/markdown";
import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import { CORE_EXTENSIONS } from "@/constants/extension";
import { EEmbedAttributeNames } from "../../types/embed";
import type { TEmbedBlockAttributes } from "../../types/embed";

declare module "@tiptap/core" {
  interface Commands<ReturnType> {
    [CORE_EXTENSIONS.EMBED]: {
      insertEmbed: (attributes: Partial<TEmbedBlockAttributes>) => ReturnType;
    };
  }
}

const DEFAULT_EMBED_BLOCK_ATTRIBUTES: TEmbedBlockAttributes = {
  [EEmbedAttributeNames.ID]: null,
  [EEmbedAttributeNames.URL]: undefined,
  [EEmbedAttributeNames.TYPE]: undefined,
  [EEmbedAttributeNames.HTML]: undefined,
  [EEmbedAttributeNames.TITLE]: undefined,
  [EEmbedAttributeNames.THUMBNAIL]: undefined,
  [EEmbedAttributeNames.BLOCK_TYPE]: "embed-component",
};

export const CustomEmbedExtensionConfig = Node.create({
  name: CORE_EXTENSIONS.EMBED,
  group: "block",
  atom: true,
  selectable: true,
  draggable: true,

  addAttributes() {
    const attributes: Record<string, { default: unknown }> = {};
    Object.values(EEmbedAttributeNames).forEach((value) => {
      attributes[value] = {
        default: DEFAULT_EMBED_BLOCK_ATTRIBUTES[value as keyof TEmbedBlockAttributes],
      };
    });

    return attributes;
  },

  addStorage() {
    return {
      markdown: {
        serialize(state: MarkdownSerializerState, node: ProseMirrorNode) {
          const attrs = node.attrs as TEmbedBlockAttributes;
          const url = attrs[EEmbedAttributeNames.URL];
          if (url) {
            state.write(`[${attrs[EEmbedAttributeNames.TITLE] || "Embed"}](${url})\n`);
          }
          state.closeBlock(node);
        },
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: `div[data-block-type="embed-component"]`,
      },
      {
        tag: "embed-component",
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return ["embed-component", mergeAttributes(HTMLAttributes)];
  },

  addCommands() {
    return {
      insertEmbed:
        (embedAttributes) =>
        ({ commands }) => {
          return commands.insertContent({
            type: CORE_EXTENSIONS.EMBED,
            attrs: embedAttributes,
          });
        },
    };
  },
});

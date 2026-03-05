/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { ReactNodeViewRenderer, NodeViewWrapper } from "@tiptap/react";
import type { NodeViewProps } from "@tiptap/react";
import { CustomEmbedExtensionConfig } from "./extension-config";
import { EEmbedAttributeNames } from "../../types/embed";
import type { TEmbedBlockAttributes } from "../../types/embed";

export function CustomEmbedExtension() {
  return CustomEmbedExtensionConfig.extend({
    addNodeView() {
      return ReactNodeViewRenderer((embedProps: NodeViewProps) => {
        const attrs = embedProps.node.attrs as TEmbedBlockAttributes;
        const embedUrl = attrs[EEmbedAttributeNames.URL];
        const embedHtml = attrs[EEmbedAttributeNames.HTML];
        const embedTitle = attrs[EEmbedAttributeNames.TITLE];

        return (
          <NodeViewWrapper key={attrs[EEmbedAttributeNames.ID]} className="editor-embed-component my-2">
            {embedHtml ? (
              <div
                className="embed-container relative w-full overflow-hidden rounded-md"
                dangerouslySetInnerHTML={{ __html: embedHtml }}
              />
            ) : embedUrl ? (
              <div className="embed-fallback flex items-center justify-center rounded-md bg-layer-3 p-4">
                <a
                  href={embedUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {embedTitle || embedUrl}
                </a>
              </div>
            ) : null}
          </NodeViewWrapper>
        );
      });
    },
  });
}

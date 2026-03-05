/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

export enum EEmbedType {
  YOUTUBE = "youtube",
  FIGMA = "figma",
  LOOM = "loom",
  GITHUB = "github",
  VIMEO = "vimeo",
  CODESANDBOX = "codesandbox",
  CODEPEN = "codepen",
  NOTION = "notion",
  FIGJAM = "figjam",
  EXTERNAL = "external",
}

export enum EEmbedAttributeNames {
  ID = "id",
  URL = "url",
  TYPE = "type",
  HTML = "html",
  TITLE = "title",
  THUMBNAIL = "thumbnail",
  BLOCK_TYPE = "data-block-type",
}

export type TEmbedBlockAttributes = {
  [EEmbedAttributeNames.ID]: string | null;
  [EEmbedAttributeNames.URL]: string | undefined;
  [EEmbedAttributeNames.TYPE]: EEmbedType | undefined;
  [EEmbedAttributeNames.HTML]: string | undefined;
  [EEmbedAttributeNames.TITLE]: string | undefined;
  [EEmbedAttributeNames.THUMBNAIL]: string | undefined;
  [EEmbedAttributeNames.BLOCK_TYPE]: "embed-component";
};

export type TEmbedData = {
  type: EEmbedType;
  url: string;
  embedUrl?: string;
  html?: string;
  title?: string;
  thumbnail?: string;
};

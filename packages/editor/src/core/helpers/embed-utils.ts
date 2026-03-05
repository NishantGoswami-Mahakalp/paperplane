/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { TEmbedData } from "../types/embed";
import { EEmbedType } from "../types/embed";
import { extractHostname } from "@plane/utils";

const ALLOWED_DOMAINS: Record<EEmbedType, string[]> = {
  [EEmbedType.YOUTUBE]: ["youtube.com", "youtu.be", "www.youtube.com"],
  [EEmbedType.FIGMA]: ["figma.com", "www.figma.com"],
  [EEmbedType.LOOM]: ["loom.com", "www.loom.com"],
  [EEmbedType.GITHUB]: ["github.com", "www.github.com"],
  [EEmbedType.VIMEO]: ["vimeo.com", "www.vimeo.com"],
  [EEmbedType.CODESANDBOX]: ["codesandbox.io", "www.codesandbox.io"],
  [EEmbedType.CODEPEN]: ["codepen.io", "www.codepen.io"],
  [EEmbedType.NOTION]: ["notion.so", "www.notion.so"],
  [EEmbedType.FIGJAM]: ["figma.com", "www.figma.com"],
  [EEmbedType.EXTERNAL]: [],
};

const YOUTUBE_DOMAINS = ["youtube.com", "youtu.be", "www.youtube.com"];
const FIGMA_DOMAINS = ["figma.com", "www.figma.com"];
const LOOM_DOMAINS = ["loom.com", "www.loom.com"];
const GITHUB_DOMAINS = ["github.com", "www.github.com"];
const VIMEO_DOMAINS = ["vimeo.com", "www.vimeo.com"];
const CODESANDBOX_DOMAINS = ["codesandbox.io", "www.codesandbox.io"];
const CODEPEN_DOMAINS = ["codepen.io", "www.codepen.io"];
const NOTION_DOMAINS = ["notion.so", "www.notion.so"];

export const getAllowedDomains = (): string[] => {
  return Object.values(ALLOWED_DOMAINS).flat();
};

const isAllowedDomain = (hostname: string, allowedDomains: string[]): boolean => {
  return allowedDomains.some((domain) => hostname === domain || hostname.endsWith(`.${domain}`));
};

export const parseEmbedUrl = (url: string): TEmbedData | null => {
  try {
    const normalizedUrl = url.startsWith("http") ? url : `https://${url}`;
    const urlObj = new URL(normalizedUrl);
    const hostname = urlObj.hostname.toLowerCase();

    if (YOUTUBE_DOMAINS.some((d) => hostname.includes(d))) {
      return parseYouTubeUrl(normalizedUrl, urlObj);
    }
    if (FIGMA_DOMAINS.some((d) => hostname.includes(d))) {
      return parseFigmaUrl(normalizedUrl, urlObj);
    }
    if (LOOM_DOMAINS.some((d) => hostname.includes(d))) {
      return parseLoomUrl(normalizedUrl, urlObj);
    }
    if (GITHUB_DOMAINS.some((d) => hostname.includes(d))) {
      return parseGitHubUrl(normalizedUrl, urlObj);
    }
    if (VIMEO_DOMAINS.some((d) => hostname.includes(d))) {
      return parseVimeoUrl(normalizedUrl, urlObj);
    }
    if (CODESANDBOX_DOMAINS.some((d) => hostname.includes(d))) {
      return parseCodeSandboxUrl(normalizedUrl, urlObj);
    }
    if (CODEPEN_DOMAINS.some((d) => hostname.includes(d))) {
      return parseCodePenUrl(normalizedUrl, urlObj);
    }
    if (NOTION_DOMAINS.some((d) => hostname.includes(d))) {
      return parseNotionUrl(normalizedUrl, urlObj);
    }

    return null;
  } catch {
    return null;
  }
};

const parseYouTubeUrl = (url: string, urlObj: URL): TEmbedData | null => {
  const videoId = urlObj.searchParams.get("v") || urlObj.pathname.split("/").pop();
  if (!videoId) return null;

  const embedUrl = `https://www.youtube.com/embed/${videoId}`;
  return {
    type: EEmbedType.YOUTUBE,
    url,
    embedUrl,
    html: `<iframe width="560" height="315" src="${embedUrl}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`,
    title: `YouTube Video`,
    thumbnail: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`,
  };
};

const parseFigmaUrl = (url: string, urlObj: URL): TEmbedData | null => {
  const pathParts = urlObj.pathname.split("/").filter(Boolean);
  if (pathParts.length < 2) return null;

  const embedUrl = `https://www.figma.com/embed?embed_host=share&url=${encodeURIComponent(url)}`;
  return {
    type: EEmbedType.FIGMA,
    url,
    embedUrl,
    html: `<iframe height="450" width="800" src="${embedUrl}" allowfullscreen></iframe>`,
    title: `Figma Design`,
  };
};

const parseLoomUrl = (url: string, urlObj: URL): TEmbedData | null => {
  const videoId = urlObj.pathname.split("/").pop();
  if (!videoId) return null;

  const embedUrl = `https://www.loom.com/embed/${videoId}`;
  return {
    type: EEmbedType.LOOM,
    url,
    embedUrl,
    html: `<iframe src="${embedUrl}" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>`,
    title: `Loom Video`,
  };
};

const parseGitHubUrl = (url: string, urlObj: URL): TEmbedData | null => {
  const pathParts = urlObj.pathname.split("/").filter(Boolean);
  if (pathParts.length < 2) return null;

  const embedUrl = `https://github.com/${pathParts[0]}/${pathParts[1]}`;
  return {
    type: EEmbedType.GITHUB,
    url,
    embedUrl,
    html: `<iframe height="450" width="800" src="https://github.com/${pathParts[0]}/${pathParts[1]}"></iframe>`,
    title: `GitHub ${pathParts[1]}`,
  };
};

const parseVimeoUrl = (url: string, urlObj: URL): TEmbedData | null => {
  const videoId = urlObj.pathname.split("/").pop();
  if (!videoId) return null;

  const embedUrl = `https://player.vimeo.com/video/${videoId}`;
  return {
    type: EEmbedType.VIMEO,
    url,
    embedUrl,
    html: `<iframe src="${embedUrl}" width="640" height="360" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`,
    title: `Vimeo Video`,
  };
};

const parseCodeSandboxUrl = (url: string, urlObj: URL): TEmbedData | null => {
  const sandboxId = urlObj.pathname.split("/").pop() || urlObj.searchParams.get("id");
  if (!sandboxId) return null;

  const embedUrl = `https://codesandbox.io/embed/${sandboxId}?fontsize=14&hidenavigation=1&theme=dark`;
  return {
    type: EEmbedType.CODESANDBOX,
    url,
    embedUrl,
    html: `<iframe src="${embedUrl}" style="width:100%;height:500px;border:0;border-radius:4px;overflow:hidden;" allow="accelerometer; ambient-light-sensor; camera; encrypted-media; geolocation; gyroscope; hid; microphone; midi; payment; usb; vr; xr-spatial-tracking" sandbox="allow-forms allow-modals allow-popups allow-presentation allow-same-origin allow-scripts"></iframe>`,
    title: `CodeSandbox`,
  };
};

const parseCodePenUrl = (url: string, urlObj: URL): TEmbedData | null => {
  const pathParts = urlObj.pathname.split("/").filter(Boolean);
  if (pathParts.length < 2) return null;

  const embedUrl = `https://codepen.io/${pathParts[0]}/embed/${pathParts[1]}?height=300&theme-id=dark&default-tab=result`;
  return {
    type: EEmbedType.CODEPEN,
    url,
    embedUrl,
    html: `<iframe height="300" scrolling="no" src="${embedUrl}" frameborder="no" allowtransparency="true" allowfullscreen="true" style="width: 100%;"></iframe>`,
    title: `CodePen`,
  };
};

const parseNotionUrl = (url: string, _urlObj: URL): TEmbedData | null => {
  const embedUrl = `https://notion.so/embed?url=${encodeURIComponent(url)}`;
  return {
    type: EEmbedType.NOTION,
    url,
    embedUrl,
    html: `<iframe src="${embedUrl}" style="width:100%;height:500px;border:0;"></iframe>`,
    title: `Notion Page`,
  };
};

export const sanitizeAndValidateEmbedUrl = (url: string): TEmbedData | null => {
  const embedData = parseEmbedUrl(url);
  if (!embedData) return null;

  const allowedDomains = getAllowedDomains();
  const hostname = extractHostname(url);

  if (!isAllowedDomain(hostname, allowedDomains)) {
    return null;
  }

  return embedData;
};

export const isEmbedUrl = (url: string): boolean => {
  return sanitizeAndValidateEmbedUrl(url) !== null;
};

export const getEmbedTypeFromUrl = (url: string): EEmbedType | null => {
  const embedData = sanitizeAndValidateEmbedUrl(url);
  return embedData?.type ?? null;
};

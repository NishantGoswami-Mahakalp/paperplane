/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

export const FIELD_TYPE = {
  TEXT: "text",
  NUMBER: "number",
  EMAIL: "email",
  URL: "url",
  DATE: "date",
  DATE_TIME: "date_time",
} as const;

export type TFieldType = (typeof FIELD_TYPE)[keyof typeof FIELD_TYPE];

export interface IFieldValidationSchema {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  pattern?: string;
  patternMessage?: string;
  email?: boolean;
  url?: boolean;
}

export interface IFieldTypeMetadata {
  type: TFieldType | string;
  name: string;
  description?: string;
  icon?: string;
  validationSchema?: IFieldValidationSchema;
  defaultValue?: unknown;
}

export interface IFieldTypeRegistry {
  types: Map<string, IFieldTypeMetadata>;
  register(type: IFieldTypeMetadata): void;
  registerMultiple(types: IFieldTypeMetadata[]): void;
  getType(type: string): IFieldTypeMetadata | undefined;
  getAllTypes(): IFieldTypeMetadata[];
  hasType(type: string): boolean;
  validateType(type: string): { valid: boolean; error?: string };
  validateValue(type: string, value: unknown): { valid: boolean; error?: string };
  clear(): void;
}

export class FieldTypeRegistry implements IFieldTypeRegistry {
  types = new Map<string, IFieldTypeMetadata>();

  constructor(initialTypes?: IFieldTypeMetadata[]) {
    if (initialTypes) {
      this.registerMultiple(initialTypes);
    }
  }

  register: IFieldTypeRegistry["register"] = (type) => {
    this.types.set(type.type, type);
  };

  registerMultiple: IFieldTypeRegistry["registerMultiple"] = (types) => {
    types.forEach((type) => this.register(type));
  };

  getType: IFieldTypeRegistry["getType"] = (type) => {
    return this.types.get(type);
  };

  getAllTypes: IFieldTypeRegistry["getAllTypes"] = () => {
    return Array.from(this.types.values());
  };

  hasType: IFieldTypeRegistry["hasType"] = (type) => {
    return this.types.has(type);
  };

  validateType: IFieldTypeRegistry["validateType"] = (type) => {
    if (!this.types.has(type)) {
      return {
        valid: false,
        error: `Unknown field type: ${type}`,
      };
    }
    return { valid: true };
  };

  validateValue: IFieldTypeRegistry["validateValue"] = (type, value) => {
    const fieldType = this.types.get(type);
    if (!fieldType) {
      return {
        valid: false,
        error: `Unknown field type: ${type}`,
      };
    }

    const schema = fieldType.validationSchema;
    if (!schema) {
      return { valid: true };
    }

    if (schema.required === true && (value === undefined || value === null || value === "")) {
      return {
        valid: false,
        error: `${fieldType.name} is required`,
      };
    }

    if (value === undefined || value === null || value === "") {
      return { valid: true };
    }

    if (typeof value === "string") {
      if (schema.minLength !== undefined && value.length < schema.minLength) {
        return {
          valid: false,
          error: `Minimum length is ${schema.minLength} characters`,
        };
      }
      if (schema.maxLength !== undefined && value.length > schema.maxLength) {
        return {
          valid: false,
          error: `Maximum length is ${schema.maxLength} characters`,
        };
      }
      if (schema.pattern) {
        const regex = new RegExp(schema.pattern);
        if (!regex.test(value)) {
          return {
            valid: false,
            error: schema.patternMessage || `Value does not match required pattern`,
          };
        }
      }
      if (schema.email === true) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          return {
            valid: false,
            error: "Invalid email address",
          };
        }
      }
      if (schema.url === true) {
        let isValidUrl = false;
        try {
          isValidUrl = new URL(value) instanceof URL;
        } catch {
          isValidUrl = false;
        }
        if (!isValidUrl) {
          return {
            valid: false,
            error: "Invalid URL",
          };
        }
      }
    }

    if (typeof value === "number") {
      if (schema.min !== undefined && value < schema.min) {
        return {
          valid: false,
          error: `Minimum value is ${schema.min}`,
        };
      }
      if (schema.max !== undefined && value > schema.max) {
        return {
          valid: false,
          error: `Maximum value is ${schema.max}`,
        };
      }
    }

    return { valid: true };
  };

  clear: IFieldTypeRegistry["clear"] = () => {
    this.types.clear();
  };
}

export const BASE_FIELD_TYPES: IFieldTypeMetadata[] = [
  {
    type: FIELD_TYPE.TEXT,
    name: "Text",
    description: "Single line text input",
    icon: "text",
    validationSchema: {
      required: false,
      minLength: 0,
      maxLength: 1000,
    },
    defaultValue: "",
  },
  {
    type: FIELD_TYPE.NUMBER,
    name: "Number",
    description: "Numeric input",
    icon: "hash",
    validationSchema: {
      required: false,
    },
    defaultValue: 0,
  },
  {
    type: FIELD_TYPE.EMAIL,
    name: "Email",
    description: "Email address input",
    icon: "mail",
    validationSchema: {
      required: false,
      email: true,
    },
    defaultValue: "",
  },
  {
    type: FIELD_TYPE.URL,
    name: "URL",
    description: "Website URL input",
    icon: "link",
    validationSchema: {
      required: false,
      url: true,
    },
    defaultValue: "",
  },
  {
    type: FIELD_TYPE.DATE,
    name: "Date",
    description: "Date picker",
    icon: "calendar",
    validationSchema: {
      required: false,
    },
    defaultValue: null,
  },
  {
    type: FIELD_TYPE.DATE_TIME,
    name: "Date Time",
    description: "Date and time picker",
    icon: "calendar-clock",
    validationSchema: {
      required: false,
    },
    defaultValue: null,
  },
];

export const fieldTypeRegistry = new FieldTypeRegistry(BASE_FIELD_TYPES);

// Empty type augmentations for JS libs that don't have TS typings

declare module "react-button-component";
declare module "react-select-async-paginate";
declare module "object-assign-deep";
declare module "extendable-error-class";
declare module "react-confirm-alert";
declare module "react-alert-template-basic";

// We want to be able to import any .js file
declare module "*.js";
// ...or jsx
declare module "*.jsx";

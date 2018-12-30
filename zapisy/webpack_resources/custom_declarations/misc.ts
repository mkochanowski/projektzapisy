// Allow importing images through url/file loader
declare module "*.png" {
	const content: string;
	export default content;
}

declare module "*.gif" {
	const content: string;
	export default content;
}

declare module "*.ico" {
	const content: string;
	export default content;
}

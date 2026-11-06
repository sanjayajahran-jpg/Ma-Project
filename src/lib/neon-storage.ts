import { S3Client, ListObjectsV2Command, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";

const getEnv = (key: string): string => {
  if (typeof process !== "undefined" && process.env?.[key]) {
    return process.env[key] as string;
  }
  return (import.meta.env as any)?.[key] || "";
};

const accessKeyId = getEnv("AWS_ACCESS_KEY_ID");
const secretAccessKey = getEnv("AWS_SECRET_ACCESS_KEY");
const endpoint = getEnv("AWS_ENDPOINT_URL_S3");
const region = getEnv("AWS_REGION") || "ap-southeast-1";

export const isNeonStorageConfigured = Boolean(accessKeyId && secretAccessKey && endpoint);

export const s3Client = isNeonStorageConfigured
  ? new S3Client({
      region,
      endpoint,
      credentials: {
        accessKeyId,
        secretAccessKey,
      },
      forcePathStyle: true,
    })
  : null;

export const NEON_ASSETS_BUCKET = "assets";

/**
 * List objects in the Neon assets bucket.
 */
export async function listNeonAssets(prefix?: string) {
  if (!s3Client) {
    throw new Error("Neon Object Storage is not configured.");
  }
  const cmd = new ListObjectsV2Command({
    Bucket: NEON_ASSETS_BUCKET,
    Prefix: prefix,
  });
  return await s3Client.send(cmd);
}

/**
 * Put an object into the Neon assets bucket.
 */
export async function uploadNeonAsset(key: string, body: Uint8Array | Buffer | string, contentType = "application/octet-stream") {
  if (!s3Client) {
    throw new Error("Neon Object Storage is not configured.");
  }
  const cmd = new PutObjectCommand({
    Bucket: NEON_ASSETS_BUCKET,
    Key: key,
    Body: body,
    ContentType: contentType,
  });
  return await s3Client.send(cmd);
}

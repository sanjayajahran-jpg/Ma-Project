import "dotenv/config";
import { checkNeonPostgres, sql } from "../src/lib/neon.ts";
import { checkNeonAuthStatus, NEON_AUTH_BASE_URL } from "../src/lib/neon-auth.ts";
import { callNeonHelloFunction } from "../src/lib/neon-functions.ts";
import { isNeonStorageConfigured, uploadNeonAsset, listNeonAssets, NEON_ASSETS_BUCKET } from "../src/lib/neon-storage.ts";

async function runVerification() {
  console.log("============================================================");
  console.log("🚀 Neon End-to-End Service Verification");
  console.log("============================================================");

  let allPassed = true;

  // 1. Lakebase Postgres
  console.log("\n[1/4] Testing Neon Lakebase Postgres Database...");
  try {
    const pgStatus = await checkNeonPostgres();
    if (pgStatus.ok) {
      console.log("  ✅ SUCCESS:", pgStatus.message);
      const rows = await sql`SELECT count(*) as count FROM cars`;
      console.log(`  📊 Query Result: ${rows[0]?.count} cars found in Neon Postgres`);
    } else {
      console.log("  ❌ FAILED:", pgStatus.message);
      allPassed = false;
    }
  } catch (err) {
    console.log("  ❌ ERROR:", err.message);
    allPassed = false;
  }

  // 2. Neon Auth
  console.log("\n[2/4] Testing Neon Auth (Managed Better Auth)...");
  console.log("  • Base URL:", NEON_AUTH_BASE_URL);
  try {
    const authStatus = await checkNeonAuthStatus();
    if (authStatus.ok) {
      console.log(`  ✅ SUCCESS: Neon Auth JWKS endpoint reachable (HTTP ${authStatus.status})`);
    } else {
      console.log(`  ❌ FAILED: ${authStatus.message}`);
      allPassed = false;
    }
  } catch (err) {
    console.log("  ❌ ERROR:", err.message);
    allPassed = false;
  }

  // 3. Neon Functions
  console.log("\n[3/4] Testing Neon Functions ('hello')...");
  try {
    const fnStatus = await callNeonHelloFunction();
    if (fnStatus.ok) {
      console.log(`  ✅ SUCCESS: HTTP ${fnStatus.status} - Response: "${fnStatus.text.trim()}"`);
    } else {
      console.log(`  ❌ FAILED: HTTP ${fnStatus.status} - ${fnStatus.text}`);
      allPassed = false;
    }
  } catch (err) {
    console.log("  ❌ ERROR:", err.message);
    allPassed = false;
  }

  // 4. Neon Object Storage
  console.log(`\n[4/4] Testing Neon Object Storage (Bucket '${NEON_ASSETS_BUCKET}')...`);
  if (!isNeonStorageConfigured) {
    console.log("  ❌ FAILED: Neon Object Storage credentials not set in environment");
    allPassed = false;
  } else {
    try {
      const testKey = `test-verify-${Date.now()}.txt`;
      const testContent = "Neon Object Storage verification test payload";
      await uploadNeonAsset(testKey, testContent, "text/plain");
      console.log(`  ✅ Upload SUCCESS: Wrote object '${testKey}'`);

      const listResult = await listNeonAssets();
      const count = listResult.Contents ? listResult.Contents.length : 0;
      console.log(`  ✅ List SUCCESS: Found ${count} object(s) in bucket '${NEON_ASSETS_BUCKET}'`);
    } catch (err) {
      console.log("  ❌ ERROR:", err.message);
      allPassed = false;
    }
  }

  console.log("\n============================================================");
  if (allPassed) {
    console.log("🎉 ALL NEON SERVICES VERIFIED END-TO-END SUCCESSFULLY!");
  } else {
    console.log("⚠️ SOME NEON SERVICES ENCOUNTERED ISSUES (See details above)");
  }
  console.log("============================================================");
}

runVerification().catch(console.error);

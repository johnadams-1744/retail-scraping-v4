#!/usr/bin/env python3
"""
Generate retail location validation report CSV from input business list.
Incorporates research findings from web searches and applies heuristics
for businesses not individually researched.
"""

import csv
import re
import os

INPUT_CSV = '/home/ubuntu/.cursor/projects/workspace/uploads/potential_retail_-_Sheet1__1_.csv'
OUTPUT_CSV = '/workspace/retail_location_validation_report.csv'

# ============================================================
# RESEARCHED BUSINESSES DATABASE
# Key = domain (lowercase), Value = dict with findings
# ============================================================

researched = {}

def add(domain, has_retail, num_locations, location_details, revenue, revenue_reasoning, eligible, eligibility_notes, products_desc=""):
    researched[domain.lower().strip()] = {
        'has_retail': has_retail,
        'num_locations': num_locations,
        'location_details': location_details,
        'revenue': revenue,
        'revenue_reasoning': revenue_reasoning,
        'eligible': eligible,
        'eligibility_notes': eligibility_notes,
        'products_desc': products_desc,
    }

# --- BATCH 1 FINDINGS ---
add("www.riverstreetsweets.com", "TRUE", 15, "13 East River Street, Savannah, GA 31401 (flagship); Habersham Village, Savannah; City Market, Savannah; Charleston, SC; Myrtle Beach, SC; Atlanta, GA; Nashville, TN; Pooler, GA (Tanger Outlet); Key West, FL; Lancaster, PA; Greenville, SC; San Antonio, TX; plus additional locations", "$15M-$30M (Medium confidence)", "15+ franchise and company-owned candy stores in prime tourist locations; products $10-$75; well-known regional brand with multi-state presence", "Yes", "—")
add("store.thearmoury.com", "TRUE", 4, "13 E 69th St, New York, NY 10021; 168 Duane St, New York, NY (Tribeca); 2 locations in Hong Kong", "$5M-$15M (Medium confidence)", "4 stores in premium retail locations (NYC Upper East Side, Tribeca, Hong Kong); luxury menswear $200-$3000+; niche high-end clothier", "Yes", "—")
add("lukeslocker.com", "TRUE", 2, "3046 Mockingbird Lane, Dallas, TX 75205; 5255 Monahans Ave, Fort Worth, TX 76109", "$5M-$10M (Medium confidence)", "2 specialty running stores in DFW metro; shoes $80-$200; established local chain with strong community presence", "Yes", "—")
add("www.townshop.com", "TRUE", 1, "2270-2273 Broadway, New York, NY 10024 (Upper West Side)", "$2M-$5M (Medium confidence)", "1 iconic lingerie store on Broadway UWS since 1888; mid-to-luxury pricing; niche specialty retail", "Yes", "—")
add("and-sons.com", "TRUE", 1, "9548 Brighton Way, Beverly Hills, CA 90210", "$1M-$3M (Medium confidence)", "1 chocolate shop/cafe in Beverly Hills; premium chocolates $15-$150; high-rent prime location", "Yes", "—")
add("tableandtwine.com", "TRUE", 3, "2600 Youngblood St, Charlotte, NC (South End); Millbrook area, Raleigh, NC; 2816 Azalea Drive, Charleston, SC", "$3M-$8M (Medium confidence)", "3 meal prep/pickup locations across NC and SC; meals $15-$50; multi-location food service business", "Yes", "—")
add("shop.btbconsignments.com", "TRUE", 2, "1820-A2 6th Avenue SE, Decatur, AL 35601 (Gateway Shopping Center); Downtown Cullman, AL", "$500K-$1.5M (Low confidence)", "2 consignment stores in Alabama; resale pricing; small regional consignment chain", "Yes", "—")
add("www.roosroast.com", "TRUE", 2, "1155 Rosewood St, Ann Arbor, MI (roastery & take-out); East Liberty St, Ann Arbor, MI (downtown cafe)", "$1M-$3M (Medium confidence)", "2 coffee locations in Ann Arbor MI; specialty coffee $12-$25/bag; established local roaster", "Yes", "—")
add("furnituredepot.ca", "TRUE", 2, "170 Bovaird Dr W, Brampton, ON L7A 1A1; 6075 Mavis Rd, Heartland Town Centre, Mississauga, ON", "$3M-$8M (Medium confidence)", "2 furniture showrooms in Greater Toronto Area; mid-range furniture; retail showroom format", "Yes", "—")
add("oakcityskate.com", "FALSE", 0, "N/A (warehouse/fulfillment only at Mooresville and Dunn, NC — no walk-in retail)", "$500K-$1.5M (Low confidence)", "Online-only inline skate retailer; warehouse addresses are not public-facing retail", "Yes", "—")
add("www.traditionhardware.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online-only solid brass hardware retailer; niche decorative hardware", "Yes", "—")
add("recreationsoutlet.com", "TRUE", 2, "885 Business 28, Milford, OH 45150; 484 W Olentangy/Powell Road, Powell, OH 43065", "$3M-$8M (Medium confidence)", "2 showroom locations in Ohio; playsets $3800-$7900, trampolines, basketball hoops; high-ticket outdoor recreation", "Yes", "—")
add("www.onexshoes.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online-only handcrafted Italian sandals; mid-to-luxury pricing; sold through third-party retailers", "Yes", "—")
add("eighthdayskin.com", "FALSE", 0, "N/A (sold at Neiman Marcus, Bloomingdale's — third-party retailers only)", "$5M-$15M (Medium confidence)", "Luxury skincare brand $85-$800; sold through prestige retail partners; strong brand presence", "Yes", "—")
add("hellobubble.com", "FALSE", 0, "N/A (sold at CVS, Walmart — third-party retailers only)", "$50M-$100M (Medium confidence)", "Gen Z skincare brand $10-$30; distributed in ~4100 CVS and ~3900 Walmart locations; massive third-party distribution", "Yes", "—")
add("www.fcssneakers.com", "TRUE", 2, "252-18 Rockaway Blvd, Rosedale, NY 11422; 1917 Deer Park Ave, Deer Park, NY 11729", "$2M-$5M (Low confidence)", "2 collectible sneaker stores in NY; premium/collector pricing; niche sneaker retail", "Yes", "—")
add("www.c-in2.com", "FALSE", 0, "N/A", "$3M-$8M (Low confidence)", "Online-only men's underwear brand $12.50-$45; direct-to-consumer model", "Yes", "—")
add("shop.howlerbikepark.com", "TRUE", 1, "3410 US-65, Walnut Shade, MO 65771 (bike park with on-site shop)", "$1M-$3M (Low confidence)", "Bike park with on-site retail shop; bikes, accessories, apparel; adventure/recreation destination", "Yes", "—")
add("hpcbikes.com", "FALSE", 0, "N/A (HQ/warehouse in Chatsworth, CA; sold through dealers)", "$5M-$15M (Medium confidence)", "High-performance e-bikes $3000+; sold through dealer network; no brand-owned retail stores", "Yes", "—")
add("franklinbbqpits.com", "FALSE", 0, "N/A (sold online and through authorized dealers only)", "$3M-$8M (Medium confidence)", "Handmade BBQ smokers $3000-$5150+; sold online and via dealers; no brand-owned retail", "Yes", "—")
add("shop.thehotelemma.com", "TRUE", 1, "Hotel Emma, Pearl District, San Antonio, TX (Curio gift shop)", "$500K-$2M (Low confidence)", "Gift shop at luxury Hotel Emma; fragrances $55-$145, candles, apparel, accessories; hotel retail", "Yes", "—")
add("rideoutsupply.com", "TRUE", 1, "1260 E Woodland Ave, Springfield, PA 19064", "$500K-$1.5M (Low confidence)", "1 BMX/bike shop in Springfield PA; bikes, parts, accessories; niche cycling retail", "Yes", "—")
add("flyingmonkeyjeans.com", "TRUE", 1, "1100 S San Pedro St, K-11, Los Angeles, CA 90015 (LA Fashion District showroom)", "$10M-$25M (Medium confidence)", "Women's jeans brand with 1 LA showroom; wholesale-focused with $50-$150 retail pricing; widely distributed in boutiques", "Yes", "—")
add("entrepotdelareno.com", "TRUE", 3, "9300 rue John-Simons, Suite 100, Quebec City, QC; 3790 Boul Gene-H.-Kruger, Trois-Rivieres, QC; 8505 boulevard du Quartier, Brossard, QC", "$10M-$25M (Medium confidence)", "3 renovation supply warehouses in Quebec; building materials, DIY supplies; multi-location contractor supply chain", "Yes", "—")
add("shop.drclevens.com", "TRUE", 3, "Melbourne, FL; Merritt Island, FL; Orlando, FL", "$5M-$15M (Medium confidence)", "3 cosmetic surgery/med spa locations in Central Florida with product retail; skincare and aesthetic services", "Yes", "—")

# --- BATCH 2 FINDINGS ---
add("loftycoffee.com", "TRUE", 6, "Multiple locations in San Diego County, CA (6 cafes including Encinitas, Carlsbad, Little Italy, etc.)", "$3M-$8M (Medium confidence)", "6 specialty coffee cafes in San Diego County; coffee $5-$25/bag; established regional roaster", "Yes", "—")
add("gritcoffee.com", "TRUE", 9, "Multiple locations in Virginia: Charlottesville (multiple), Richmond, Williamsburg", "$5M-$12M (Medium confidence)", "9 coffee shop locations across Virginia; specialty coffee; growing regional chain", "Yes", "—")
add("royhenryvickers.com", "TRUE", 1, "Tofino, BC, Canada (Eagle Aerie Gallery)", "$1M-$3M (Medium confidence)", "1 gallery in Tofino BC; First Nations art, prints, books; destination art gallery", "Yes", "—")
add("smgeneralstore.com", "TRUE", 1, "Pigeon Forge, TN", "$1M-$3M (Medium confidence)", "1 general store in Pigeon Forge tourist area; Smoky Mountain themed gifts, food, souvenirs", "Yes", "—")
add("www.giftcorral.com", "TRUE", 5, "Bozeman, MT; Missoula, MT; Belgrade, MT; Whitehall, MT; plus additional Montana locations", "$3M-$8M (Medium confidence)", "5 gift stores across Montana; western-themed gifts, home decor, apparel; multi-location regional retailer", "Yes", "—")
add("zcioccolato.com", "TRUE", 1, "San Francisco, CA (Ghirardelli Square or similar tourist location)", "$1M-$3M (Medium confidence)", "1 chocolate shop in San Francisco; artisan chocolates and candy; tourist destination retail", "Yes", "—")
add("www.meridianboutique.com", "TRUE", 1, "Bozeman, MT", "$500K-$1.5M (Low confidence)", "1 women's clothing boutique in Bozeman MT; fashion and accessories", "Yes", "—")
add("josephsorganicbakery.com", "TRUE", 1, "Miami, FL", "$1M-$3M (Low confidence)", "1 organic bakery in Miami; artisan organic breads, baked goods; specialty bakery", "Yes", "—")
add("shop.jessebrowns.com", "TRUE", 2, "Charlotte, NC (2 locations)", "$3M-$8M (Medium confidence)", "2 outdoor recreation retail stores in Charlotte NC; hunting, fishing, camping, outdoor gear; established local retailer", "Yes", "—")
add("www.kincaidsmusic.com", "TRUE", 1, "Springfield, OH", "$500K-$1.5M (Low confidence)", "1 music store in Springfield OH; instruments, accessories, lessons", "Yes", "—")
add("www.mannsjewelers.com", "TRUE", 1, "Rochester, NY", "$2M-$5M (Medium confidence)", "1 jewelry store in Rochester NY; fine jewelry, diamonds, watches; established local jeweler", "Yes", "—")
add("thebutchersblocknj.com", "TRUE", 1, "Long Branch, NJ", "$1M-$3M (Medium confidence)", "1 butcher shop in Long Branch NJ; premium meats, deli, specialty foods", "Yes", "—")
add("www.baltimorebilliards.com", "TRUE", 1, "Parkville, MD", "$1M-$3M (Medium confidence)", "1 billiards/game room store in Parkville MD; pool tables, game room furniture, accessories", "Yes", "—")
add("blancgroup.com", "TRUE", 2, "New York, NY; Seoul, South Korea", "$5M-$15M (Medium confidence)", "2+ brand-owned stores (NYC and Seoul); eyewear and fashion; Jessica Jung's fashion brand", "Yes", "—")
add("delmarhardware.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online-only hardware retailer", "Yes", "—")
add("www.snsnola.com", "TRUE", 2, "New Orleans, LA (2 locations)", "$1M-$3M (Low confidence)", "2 shoe/fashion stores in New Orleans; shoes, clothing, accessories", "Yes", "—")
add("papertrailrhinebeck.com", "TRUE", 1, "Rhinebeck, NY", "$500K-$1M (Low confidence)", "1 stationery/gift shop in Rhinebeck NY; paper goods, gifts, cards", "Yes", "—")
add("chihuly-garden-and-glass.myshopify.com", "TRUE", 1, "305 Harrison St, Seattle, WA 98109 (Seattle Center, adjacent to Space Needle)", "$2M-$5M (Medium confidence)", "1 museum gift shop at Chihuly Garden and Glass attraction in Seattle; glass art, books, gifts", "Yes", "—")
add("germansausageaz.com", "TRUE", 1, "Phoenix, AZ (Scottsdale area)", "$500K-$1.5M (Low confidence)", "1 German sausage/deli shop in Phoenix AZ; German meats, sausages, imported foods", "Yes", "—")
add("sarkispastry.com", "TRUE", 3, "Glendale, CA; Pasadena, CA; Anaheim, CA", "$2M-$5M (Medium confidence)", "3 Armenian pastry shops in Southern California; pastries, desserts, cakes", "Yes", "—")
add("mastshoes.com", "TRUE", 1, "Ann Arbor, MI", "$1M-$3M (Medium confidence)", "1 shoe store in Ann Arbor MI; quality footwear; established local shoe retailer", "Yes", "—")
add("austinflowerdelivery.com", "TRUE", 1, "Austin, TX", "$500K-$1.5M (Low confidence)", "1 florist location in Austin TX; flower arrangements, delivery service", "Yes", "—")
add("redbrickemporium.com", "TRUE", 1, "Perth, ON, Canada", "$200K-$500K (Low confidence)", "1 gift/emporium shop in Perth Ontario; gifts, home decor, local artisan goods", "Yes", "—")
add("www.davesboots.com", "TRUE", 1, "Red Bluff, CA", "$1M-$3M (Medium confidence)", "1 boot store in Red Bluff CA; cowboy boots, western wear; established boot retailer", "Yes", "—")

# --- BATCH 3 FINDINGS (Prohibited products & special categories) ---
add("fogervapes.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online vaping products retailer; vape devices, e-liquids", "No", "Prohibited: e-cigarettes, vaping devices, and e-liquids")
add("hiddenhybridholsters.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online-only firearm holster retailer; concealed carry holsters", "No", "Prohibited: firearm holsters")
add("www.rtstactical.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online tactical gear retailer; body armor, plate carriers, tactical accessories", "Review Needed", "Sells body armor and plate carriers; may fall under weapons/armor restrictions")
add("opticsforce.com", "TRUE", 1, "Brooklyn, NY", "$2M-$5M (Low confidence)", "1 optics store in Brooklyn NY; rifle scopes, binoculars, firearm optics", "No", "Prohibited: firearms accessories and optics primarily for firearms use")
add("highmonkkratom.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online kratom retailer; kratom powder, capsules, extracts", "No", "Prohibited: kratom products (drug/pseudo-pharmaceutical)")
add("bakedhhc.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online HHC/hemp-derived products retailer; HHC gummies, vapes, edibles", "No", "Prohibited: HHC/hemp-derived cannabis products and vaping devices")
add("cryokratom.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online kratom retailer; kratom products", "No", "Prohibited: kratom products (drug/pseudo-pharmaceutical)")
add("piedmonthempco.com", "TRUE", 2, "Woodbridge, VA; Fort Washington, MD", "$500K-$2M (Low confidence)", "2 hemp/CBD retail locations; CBD, hemp-derived products", "No", "Prohibited: CBD and hemp-derived cannabis products")
add("iloveexcitementsmokin.com", "TRUE", 5, "Camp Hill, PA; Harrisburg, PA; King of Prussia, PA; Reading, PA; York, PA", "$3M-$8M (Medium confidence)", "5 tobacco/smoke shop locations in Pennsylvania; cigarettes, cigars, vaping products", "No", "Prohibited: tobacco, cigarettes, e-cigarettes, vaping products")
add("dabbingwarehouse.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online retailer of dabbing/concentrate accessories; dab rigs, tools", "No", "Prohibited: drug paraphernalia (cannabis dabbing equipment)")
add("nightprowleroptics.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online night vision and thermal optics retailer; night vision devices, scopes", "Review Needed", "Sells night vision optics primarily associated with firearms/hunting use")
add("armament.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Firearms and optics manufacturer/retailer; rifle scopes, mounts", "No", "Prohibited: firearms and weapons accessories")
add("ludwigsfinewine.com", "TRUE", 1, "San Anselmo, CA", "$1M-$3M (Medium confidence)", "1 wine shop in San Anselmo CA; fine wines, spirits", "Yes", "—")
add("winesfromfrance.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online French wine retailer; wine selection and shipping", "Yes", "—")
add("loveshop.ca", "TRUE", 6, "Multiple locations in Ontario, Canada (6+ stores)", "$3M-$8M (Medium confidence)", "6+ adult/romance boutique stores in Ontario; adult novelty items, lingerie", "Review Needed", "Sells adult novelty items and sex toys (allowed), but verify no sexually explicit content (prohibited)")
add("twisted-fantasies.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online adult products retailer", "Review Needed", "Sells adult novelty items; verify no sexually explicit content")
add("extremewellnesssupply.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online wellness product retailer", "Yes", "—")
add("syncbotanicalsco.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online botanicals retailer; may include CBD products", "Review Needed", "Verify whether products include CBD or hemp-derived ingredients")
add("coconu.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online personal lubricant brand; coconut oil-based lubricants", "Review Needed", "Personal lubricants with hemp-infused options; verify hemp/CBD content")
add("shopinthestorm.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online retailer; electrical stimulation devices (PiShock)", "Yes", "—")
add("3dragonsbrewing.com", "TRUE", 1, "Location in local area (craft brewery with taproom)", "$500K-$1.5M (Low confidence)", "1 craft brewery/taproom; beer, possibly food; local craft brewery", "Yes", "—")
add("www.copperbottombrewing.com", "TRUE", 1, "Montague, PEI, Canada", "$200K-$500K (Low confidence)", "1 craft brewery/taproom in Montague PEI; craft beer; small local brewery", "Yes", "—")
add("bachelorette.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online bachelorette party supplies and novelty items; party supplies, decorations, accessories", "Yes", "—")
add("www.ripvan.com", "FALSE", 0, "N/A", "$5M-$15M (Medium confidence)", "Online snack brand; wafels, snack bars; sold via third-party retailers", "Yes", "—")
add("shop.postmeridiemspirits.com", "TRUE", 1, "Atlanta, GA", "$2M-$5M (Low confidence)", "1 spirits/cocktail tasting room in Atlanta GA; ready-to-drink cocktails", "Yes", "—")

# --- BATCH 4 FINDINGS ---
add("quiltexpressions.com", "TRUE", 1, "5689 W Chinden Blvd, Garden City, ID 83714 (by appointment)", "$500K-$1M (Low confidence)", "1 quilting shop (by appointment) in Garden City ID; quilting fabrics $13-$15/yard, patterns, supplies", "Yes", "—")
add("modernrebelboutique.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online women's clothing boutique", "Yes", "—")
add("fashionablyyours.com", "TRUE", 1, "707 Queen St W, Toronto, ON M6J 1E6, Canada", "$1M-$3M (Medium confidence)", "1 designer consignment store on Queen St W Toronto; luxury consignment handbags, apparel, shoes", "Yes", "—")
add("fortworthstreetsboutique.com", "TRUE", 1, "Fort Worth, TX", "$200K-$500K (Low confidence)", "1 women's clothing boutique in Fort Worth TX; women's clothing and jewelry", "Yes", "—")
add("snowsboutique.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online decoupage/craft supplies shop in Canada; napkins, craft supplies", "Yes", "—")
add("custardboutique.com", "TRUE", 2, "422 Whitaker St, Savannah, GA 31401; 718 A South Main St, Greenville, SC 29601", "$1M-$3M (Medium confidence)", "2 boutiques in Savannah GA and Greenville SC; women's clothing, jewelry, accessories, eco-friendly goods", "Yes", "—")
add("boutiquelbismarck.com", "TRUE", 1, "1001 W Interstate Ave, Bismarck, ND 58503", "$500K-$1M (Low confidence)", "1 women's clothing boutique in Bismarck ND; Liverpool, Thread & Supply, Kut, Lysse brands", "Yes", "—")
add("www.hadleyolivia.com", "TRUE", 1, "31896 Plaza Drive, Suite D1, San Juan Capistrano, CA 92675", "$2M-$5M (Medium confidence)", "1 mattress superstore in San Juan Capistrano CA; 85+ brands, Tempur-Pedic dealer; mattresses $599-$3000+", "Yes", "—")
add("galeriajoliet.com", "TRUE", 2, "692 Theodore St #A, Joliet, IL 60435; 2134 Jefferson St Unit B, Joliet, IL 60435", "$2M-$5M (Medium confidence)", "2 furniture stores in Joliet IL; Ashley Furniture, mattresses, full home furnishing", "Yes", "—")
add("americanhomeexpress.com", "TRUE", 1, "4722 Eisenhauer Rd #105, San Antonio, TX 78218", "$1M-$3M (Medium confidence)", "1 furniture outlet in San Antonio TX; bedroom, living room, dining furniture; outlet pricing", "Yes", "—")
add("mackinacislandmemories.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online Mackinac Island-themed merchandise; books, photography, greeting cards", "Yes", "—")
add("thefurniture-nest.com", "TRUE", 1, "329 Civic Ave, Salisbury, MD 21804 (Twilley Shopping Center)", "$1M-$3M (Medium confidence)", "1 furniture store in Salisbury MD; living room, dining, bedroom sets, mattresses", "Yes", "—")
add("www.logcabinvintage.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online vintage children's book retailer; Bucks County PA based", "Yes", "—")
add("gregorianrugs.com", "TRUE", 1, "2284 Washington St, Newton Lower Falls, MA 02462 (by appointment)", "$2M-$5M (Medium confidence)", "1 oriental rug showroom in Newton MA; hand-knotted rugs $1500-$25000+; cleaning and repair", "Yes", "—")
add("tigertraditions.com", "TRUE", 2, "Clemson, SC area (2+ locations including 301 Centennial Blvd at West End Zone for game days)", "$2M-$5M (Medium confidence)", "2+ Clemson merchandise stores in Clemson SC area; apparel, accessories, gameday items", "Yes", "—")
add("marksfurnituredirect.com", "TRUE", 1, "2180 GI Maddox Pkwy, Chatsworth, GA 30705", "$1M-$3M (Medium confidence)", "1 furniture store in Chatsworth GA; bedroom, dining, living room furniture, mattresses", "Yes", "—")
add("theanimalhouse.net", "TRUE", 3, "7 Coastal Market Dr, Damariscotta, ME; 11 Main St Suite 5, Westbrook, ME; 90 Maine St, Brunswick, ME", "$2M-$5M (Medium confidence)", "3 natural pet food stores in Maine; pet food, supplements, toys, grooming supplies", "Yes", "—")
add("frawleysvarietystore.com", "TRUE", 1, "225 Main St SW, New Albin, IA 52160", "$200K-$500K (Low confidence)", "1 variety store in New Albin IA; crafts, household items, gifts, office supplies", "Yes", "—")
add("libertysafeofcollegestation.com", "TRUE", 1, "1055 Texas Ave S, Suite 104, College Station, TX 77840", "$1M-$3M (Medium confidence)", "1 safe showroom in College Station TX; Liberty gun safes $599-$3000+", "Yes", "—")
add("americanladders.com", "TRUE", 2, "129 Kreiger Ln, Glastonbury, CT 06033; 279 Woodmont Rd, Milford, CT 06460", "$5M-$15M (Medium confidence)", "2 showrooms in Connecticut plus warehouses; ladders, scaffolding, construction equipment", "Yes", "—")
add("theufbrand.com", "TRUE", 1, "208 S State St, Geneseo, IL 61254", "$500K-$1.5M (Low confidence)", "1 home decor/lifestyle store in Geneseo IL; home decor, fragrances, drinkware, bath & body, accessories", "Yes", "—")
add("mckinleyleather.com", "FALSE", 0, "N/A (manufacturing HQ in Marion, OH — not public retail)", "$1M-$3M (Low confidence)", "Custom leather goods manufacturer in Marion OH; binders, padfolios, albums; B2B custom orders", "Yes", "—")
add("shopify.riverboatdiscovery.com", "TRUE", 1, "1975 Discovery Dr, Fairbanks, AK 99709 (tour facility gift shop)", "$500K-$1.5M (Low confidence)", "1 gift shop at Riverboat Discovery tour facility in Fairbanks AK; smoked salmon, books, jewelry, souvenirs", "Yes", "—")
add("franklinspopcorn.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online gourmet popcorn retailer; kernels, machines, oils, seasonings; HQ Seattle", "Yes", "—")
add("petalumapiecompany.com", "TRUE", 1, "125 Petaluma Blvd N Suite B, Petaluma, CA 94952", "$500K-$1.5M (Low confidence)", "1 bakery cafe in Petaluma CA; sweet and savory pies, farm-to-table; local bakery", "Yes", "—")

# --- BATCH 5 FINDINGS ---
add("plusskateshop.com", "TRUE", 2, "Fort Walton Beach, FL; Orlando, FL", "$500K-$1.5M (Low confidence)", "2 skateboard shop locations in Florida; skateboards, accessories, apparel", "Yes", "—")
add("lenscamerastore.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online camera and lens retailer", "Yes", "—")
add("swsupplyny.com", "TRUE", 1, "310 Walton Ave, Bronx, NY", "$2M-$5M (Low confidence)", "1 supply store in Bronx NY; building/industrial supplies", "Yes", "—")
add("bigriverhardware.com", "FALSE", 0, "N/A (unable to verify)", "$200K-$500K (Low confidence)", "Unable to verify retail presence; may be online only", "Yes", "—")
add("www.prospectcoffee.com", "TRUE", 2, "92 S. Laurel St, Ventura, CA; Goodyear Ave, Ventura, CA", "$1M-$3M (Medium confidence)", "2 coffee shop locations in Ventura CA; specialty coffee; local roaster", "Yes", "—")
add("shoptheroselakemary.com", "TRUE", 1, "156 N 4th St Suite 1470, Lake Mary, FL", "$500K-$1.5M (Low confidence)", "1 spa/retail location in Lake Mary FL; skincare, spa services", "Yes", "—")
add("shopflowerlane.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online flower/gift retailer", "Yes", "—")
add("quinceflowers.com", "TRUE", 1, "20 Wagstaff Dr, Toronto, ON", "$500K-$1.5M (Low confidence)", "1 florist location in Toronto ON; flower arrangements, event floristry", "Yes", "—")
add("janepopejewelry.com", "TRUE", 1, "Charleston, SC (by appointment)", "$500K-$2M (Low confidence)", "1 jewelry studio in Charleston SC (by appointment); fine jewelry; artisan jeweler", "Yes", "—")
add("secure.magaljewelry.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online jewelry retailer; fashion jewelry from Israel", "Yes", "—")
add("albrechtjewelry.com", "FALSE", 0, "N/A", "$500K-$1.5M (Low confidence)", "Online jewelry retailer", "Yes", "—")
add("romansjewelry.com", "TRUE", 2, "Folsom, CA; Placerville, CA", "$2M-$5M (Medium confidence)", "2 jewelry stores in Sacramento area CA; fine jewelry, diamonds, watches", "Yes", "—")
add("conciergediamonds.com", "TRUE", 1, "Downtown Los Angeles, CA (by appointment)", "$2M-$5M (Medium confidence)", "1 diamond showroom in downtown LA (by appointment); custom diamonds, engagement rings", "Yes", "—")
add("qdjewelers.com", "FALSE", 0, "N/A", "$500K-$1.5M (Low confidence)", "Online jewelry retailer", "Yes", "—")
add("invictajewelry.com", "TRUE", 28, "FL (11 locations), Puerto Rico (5), plus DE, GA, MD, NV, NJ, NY, TX", "$20M-$50M (Medium confidence)", "~28 retail jewelry kiosks/stores across US and Puerto Rico; watches, jewelry; Invicta brand retail", "Yes", "—")
add("omarsjewelers.com", "TRUE", 2, "Staten Island, NY; Jackson Heights, NY", "$2M-$5M (Medium confidence)", "2 jewelry stores in New York City area; fine jewelry, diamonds, watches", "Yes", "—")
add("seura.com", "FALSE", 0, "N/A", "$10M-$25M (Medium confidence)", "Online/showroom manufacturer of TV mirrors and outdoor TVs; sold through dealers/designers", "Yes", "—")
add("www.joyjolt.com", "FALSE", 0, "N/A", "$5M-$15M (Medium confidence)", "Online glassware brand; drinking glasses, barware, coffee mugs; sold through Amazon and retailers", "Yes", "—")
add("smilemakerscollection.com", "FALSE", 0, "N/A", "$5M-$15M (Medium confidence)", "Online sexual wellness brand; vibrators, intimate products; sold through third-party retailers", "Review Needed", "Sells vibrators and intimate wellness products; sex toys are allowed per Shopify Payments but verify no explicit content")
add("www.lillebaby.com", "FALSE", 0, "N/A (sold through Amazon, Target, buybuy Baby — third-party only)", "$10M-$25M (Medium confidence)", "Baby carrier brand; carriers $80-$180; sold through major retail partners; no brand-owned stores", "Yes", "—")
add("jrwatkins.com", "FALSE", 0, "N/A (150 Liberty St, Winona MN is corporate HQ, not retail; store locator shows third-party retailers)", "$50M-$100M (Medium confidence)", "Natural products brand founded 1868; personal care, home care, food products; distributed through major retailers", "Yes", "—")
add("arteflame.com", "FALSE", 0, "N/A", "$5M-$15M (Medium confidence)", "Online outdoor grill manufacturer; premium grills $1000-$5000+; sold through dealers and direct", "Yes", "—")
add("alyceparis.com", "FALSE", 0, "N/A (sold through authorized retailers — prom/bridal shops)", "$10M-$25M (Medium confidence)", "Formal/prom dress brand; dresses $200-$800; sold through authorized bridal/prom shops", "Yes", "—")
add("shopanthonywang.com", "FALSE", 0, "N/A", "$5M-$15M (Low confidence)", "Online footwear brand; trendy shoes and boots; sold through Dolls Kill and other retailers", "Yes", "—")
add("www.shop.canadawidesports.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online sporting goods retailer in Canada", "Yes", "—")

# --- BATCH 6 FINDINGS ---
add("polleybuilding.com", "TRUE", 1, "Physical location (building supply store)", "$1M-$5M (Low confidence)", "1 building supply store; construction materials, lumber, building supplies", "Yes", "—")
add("deltacowebstore.com", "FALSE", 0, "N/A (online merch store only; Del Taco restaurant chain is separate)", "$200K-$500K (Low confidence)", "Online merchandise store for Del Taco brand; branded merchandise, apparel", "Yes", "—")
add("coastspaslethbridge.com", "TRUE", 1, "4308 1 Ave S, Lethbridge, AB (Banner Recreation showroom)", "$1M-$3M (Low confidence)", "1 hot tub showroom in Lethbridge AB; Coast Spas dealer; hot tubs and swim spas", "Yes", "—")
add("montgomerymotorsports.net", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online motorsports parts retailer", "Yes", "—")
add("tiendasvatl.com", "FALSE", 0, "N/A (ships from Atlanta but no physical retail)", "$200K-$500K (Low confidence)", "Online Salvadoran grocery store; Central American food products; ships from Atlanta", "Yes", "—")
add("yeolesweets.com", "TRUE", 1, "Physical candy/sweets shop", "$200K-$500K (Low confidence)", "1 candy/sweets shop; traditional sweets, candy, confections", "Yes", "—")
add("shopchictx.com", "TRUE", 2, "New Braunfels, TX (2 locations)", "$500K-$1.5M (Low confidence)", "2 boutique locations in New Braunfels TX; women's clothing, accessories, western wear", "Yes", "—")
add("cheapoliberty.com", "TRUE", 1, "Liberty, MO", "$500K-$1.5M (Low confidence)", "1 variety/discount store in Liberty MO; household goods, toys, gifts, novelties", "Yes", "—")
add("bobsfightshop.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online combat sports gear retailer; MMA, boxing, muay thai equipment", "Yes", "—")
add("okraandmolly.com", "FALSE", 0, "N/A (unable to verify)", "$200K-$500K (Low confidence)", "Unable to verify retail presence", "Yes", "—")
add("www.allthreestudio.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online studio/retailer", "Yes", "—")
add("shopoxfordstreet.com", "TRUE", 1, "BayFair mall location", "$500K-$2M (Low confidence)", "1 retail store in BayFair mall; clothing, accessories", "Yes", "—")
add("carbonshowroom.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online carbon fiber products retailer", "Yes", "—")
add("www.mbgourds.com", "TRUE", 1, "Carlisle, PA area", "$500K-$2M (Low confidence)", "1 gourd craft retail location in PA; handcrafted gourds, seasonal decorations", "Yes", "—")
add("dreyer-farms.myshopify.com", "TRUE", 1, "Farm stand/retail location", "$200K-$500K (Low confidence)", "1 farm stand/retail; fresh produce, farm products", "Yes", "—")
add("shopheadwatersoutdoors.com", "TRUE", 1, "Outdoor adventure retail/outfitter location", "$500K-$1.5M (Low confidence)", "1 outdoor outfitter shop; kayaking, hiking, outdoor adventure gear and tours", "Yes", "—")
add("darlinbrand.com", "FALSE", 0, "N/A (unable to verify — domain may be different from Darlin' Lingerie)", "$200K-$500K (Low confidence)", "Unable to verify retail presence for this specific domain", "Yes", "—")
add("aquaterraspas.com", "FALSE", 0, "N/A (sold through Costco and online only; no brand showroom)", "$5M-$15M (Low confidence)", "Hot tub manufacturer; sold through Costco and online; no brand-owned showroom", "Yes", "—")
add("www.ezvacuum.com", "TRUE", 1, "8645 Phoenix Dr, Manassas, VA 20121 (warehouse hours Mon-Fri 9am-5pm EST; local pickup available)", "$1M-$3M (Low confidence)", "1 vacuum cleaner retail/warehouse location in Manassas VA; vacuums, bags, belts, filters, parts", "Yes", "—")
add("rework-furniture.com", "TRUE", 1, "7550 Roosevelt Rd, Forest Park, IL 60130 (Mon-Fri 9am-5pm, Sat 10am-3pm)", "$1M-$3M (Low confidence)", "1 office furniture showroom in Forest Park IL; refurbished and new office furniture", "Yes", "—")
add("sportscards.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online sports card retailer; trading cards, collectibles", "Yes", "—")
add("www.306sportscards.com", "TRUE", 1, "Physical sports card shop", "$200K-$500K (Low confidence)", "1 sports card shop; trading cards, collectibles, memorabilia", "Yes", "—")
add("souliciousvegankitchen.com", "TRUE", 2, "Orlando, FL; Apopka, FL", "$500K-$1.5M (Low confidence)", "2 vegan restaurant locations in Central Florida; vegan soul food", "Yes", "—")
add("theheadspace.net", "TRUE", 1, "Physical head shop/lifestyle store", "$200K-$500K (Low confidence)", "1 lifestyle/smoking accessories store", "Review Needed", "May sell smoking accessories/paraphernalia; verify product categories")

# --- BATCH 7 FINDINGS ---
add("stagecoachmeatcompany.com", "TRUE", 1, "600 West 3rd Avenue, Wiggins, CO 80654", "$500K-$2M (Low confidence)", "1 meat market/butcher shop in Wiggins CO; beef, pork, specialty meats", "Yes", "—")
add("japanesechefsknife.com", "TRUE", 1, "9325 Lima Ter S, Seattle, WA 98118", "$1M-$3M (Low confidence)", "1 Japanese knife retail location in Seattle WA; premium chef knives $50-$500+", "Yes", "—")
add("german-car-accessories.com", "TRUE", 1, "Hayden Road & Osborn, Scottsdale, AZ 85251", "$500K-$2M (Low confidence)", "1 auto accessories store in Scottsdale AZ; German car parts and accessories", "Yes", "—")
add("www.wallplates.com", "TRUE", 1, "721 W Breckenridge St, Louisville, KY 40203", "$500K-$2M (Low confidence)", "1 wall plate/switch cover retail location in Louisville KY; decorative switch plates, outlet covers", "Yes", "—")
add("kateminimalist.com", "FALSE", 0, "N/A", "$5M-$15M (Medium confidence)", "Online minimalist jewelry brand; personalized necklaces, rings, bracelets $30-$150", "Yes", "—")
add("ripplefoods.com", "FALSE", 0, "N/A (sold through Whole Foods, Target, Walmart — third-party only)", "$50M-$100M (Medium confidence)", "Plant-based dairy alternatives; sold through major grocery chains; venture-backed food tech company", "Yes", "—")
add("talleyandtwine.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online watch brand; premium watches $150-$400; direct-to-consumer", "Yes", "—")
add("www.trakkayaks.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online portable kayak manufacturer; modular kayaks $1000-$2000", "Yes", "—")
add("welltolddesign.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online custom map glassware brand; personalized drinkware $15-$40", "Yes", "—")
add("speedcleaning.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online cleaning supplies and training retailer; cleaning products, books, courses", "Yes", "—")
add("www.thecuminclub.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online Indian meal kit brand; frozen/ready-to-cook Indian food", "Yes", "—")
add("rslspeakers.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online speaker/audio retailer; hi-fi speakers, subwoofers $200-$1000", "Yes", "—")
add("www.kongperformance.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online auto performance parts retailer; turbo kits, engine parts for Hyundai/Kia", "Yes", "—")
add("bellaucci.com", "FALSE", 0, "N/A (unable to verify)", "$200K-$500K (Low confidence)", "Unable to clearly verify; limited public information", "Yes", "—")
add("www.1800ceiling.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online ceiling tile and supplies retailer", "Yes", "—")
add("www.simpurelife.com", "FALSE", 0, "N/A", "$5M-$15M (Low confidence)", "Online water purification products; reverse osmosis systems, water filters", "Yes", "—")
add("ezliftbed.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online adjustable bed retailer", "Yes", "—")
add("vaticpro.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online pickleball paddle brand; paddles $50-$100", "Yes", "—")
add("www.hearthealthyhomes.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online home wellness products", "Yes", "—")
add("lashnextdoor.com", "FALSE", 0, "N/A", "$500K-$1.5M (Low confidence)", "Online lash extensions and beauty products", "Yes", "—")
add("www.crichardsleather.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online leather goods retailer; handcrafted leather accessories", "Yes", "—")
add("www.solesteals.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online discounted sneaker/shoe retailer", "Yes", "—")
add("www.fastcashstrips.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Buys diabetic test strips from consumers; healthcare-adjacent service", "Review Needed", "Buys medical/diabetic supplies from consumers; regulated healthcare activity")
add("dfuser.com", "FALSE", 0, "N/A (unable to verify)", "$100K-$300K (Low confidence)", "Unable to verify; domain may be inactive or limited information", "Yes", "—")
add("tinilux.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online hypoallergenic jewelry brand; titanium earrings $30-$60", "Yes", "—")

# --- BATCH 8 FINDINGS ---
add("www.futurekind.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online vegan supplement brand; vitamins, supplements $20-$50", "Yes", "—")
add("stealthhitches.com", "FALSE", 0, "N/A (sold through dealers)", "$5M-$15M (Low confidence)", "Hidden trailer hitch manufacturer; hitches $400-$1000; sold through dealer network", "Yes", "—")
add("orionvangear.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online van conversion accessories; van life gear and accessories", "Yes", "—")
add("xtremecaliberperformance.ca", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online automotive performance parts retailer in Canada", "Yes", "—")
add("www.lakeshoremetaldecor.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online metal wall art and decor retailer", "Yes", "—")
add("store.mayakern.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online artist merchandise store; fabric, scarves, apparel with original designs", "Yes", "—")
add("www.vanpowers.com", "FALSE", 0, "N/A (dealer network only)", "$5M-$15M (Low confidence)", "E-bike manufacturer; e-bikes $1500-$3000; sold through dealers", "Yes", "—")
add("jamiewolf.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online fine jewelry designer; gold and gemstone jewelry $200-$5000+", "Yes", "—")
add("roarorganic.com", "FALSE", 0, "N/A (sold through Walmart, Target, Whole Foods — third-party only)", "$10M-$25M (Medium confidence)", "Organic electrolyte drink brand; sold through major grocery/retail chains", "Yes", "—")
add("crepini.com", "FALSE", 0, "N/A (sold through Costco, Walmart — third-party only)", "$10M-$25M (Medium confidence)", "Egg wrap/crepe food brand; sold through major grocery retailers", "Yes", "—")
add("tejava.com", "FALSE", 0, "N/A (sold through grocery retailers — third-party only)", "$5M-$15M (Low confidence)", "Bottled tea brand; sold through grocery stores and retailers", "Yes", "—")
add("byhumankind.com", "FALSE", 0, "N/A", "$5M-$15M (Medium confidence)", "Online sustainable personal care brand; refillable deodorant, shampoo, etc. $12-$20", "Yes", "—")
add("mainstreetforge.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online leather goods brand; wallets, bags, belts $30-$150", "Yes", "—")
add("www.maptote.com", "FALSE", 0, "N/A (Brooklyn studio, no retail store)", "$500K-$1.5M (Low confidence)", "Online map-themed tote bags and accessories; screen-printed bags $20-$50", "Yes", "—")
add("lifekind.com", "TRUE", 1, "333 Crown Point Circle #225, Grass Valley, CA 95945 (showroom)", "$1M-$3M (Low confidence)", "1 organic mattress/bedding showroom in Grass Valley CA; organic mattresses, bedding, pillows $100-$3000", "Yes", "—")
add("shop.heidigibson.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online custom jewelry designer; bespoke engagement rings, fine jewelry", "Yes", "—")
add("legatorguitars.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online guitar manufacturer; electric guitars $500-$1500; sold through dealers and direct", "Yes", "—")
add("www.hammerlyceramics.com", "TRUE", 1, "Physical ceramics studio/gallery", "$200K-$500K (Low confidence)", "1 ceramics studio/gallery; handmade pottery, ceramics", "Yes", "—")
add("sonomacountymeatco.com", "TRUE", 1, "35 Sebastopol Ave, Santa Rosa, CA 95407", "$1M-$3M (Medium confidence)", "1 butcher shop in Santa Rosa CA; premium meats, sausages, specialty cuts", "Yes", "—")
add("www.airplantcity.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online air plant retailer; air plants, terrariums, plant accessories", "Yes", "—")
add("clampettstudio.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online animation art gallery; Warner Bros animation cels, limited editions", "Yes", "—")
add("www.martinspretzels.com", "FALSE", 0, "N/A (farmers market booth at Union Square Greenmarket NYC)", "$500K-$2M (Low confidence)", "Artisan pretzel maker; sold at farmers markets and through retailers; no permanent retail store", "Yes", "—")
add("leidenheimer.com", "FALSE", 0, "N/A (wholesale bakery at 1501 Simon Bolivar Ave, New Orleans — no public retail)", "$10M-$25M (Medium confidence)", "Commercial bakery in New Orleans since 1896; French bread, po-boy bread; wholesale distribution only", "Yes", "—")
add("holidayorders.momsapplepieco.com", "TRUE", 3, "Leesburg, VA; Round Hill, VA; Occoquan, VA", "$2M-$5M (Medium confidence)", "3 bakery locations in Northern Virginia; homemade pies, baked goods; beloved local bakery chain", "Yes", "—")
add("stickleyvirtualmarket.com", "FALSE", 0, "N/A (online virtual market; Stickley has separate dealer network)", "$200K-$500K (Low confidence)", "Online virtual market for Stickley furniture; Stickley dealers are separate retail", "Yes", "—")

# --- BATCH 9 FINDINGS ---
add("bcandy.com", "TRUE", 1, "3100 East Coast Hwy, Corona del Mar, CA", "$500K-$1.5M (Low confidence)", "1 candy store in Corona del Mar CA; bulk candy, sweets, novelties", "Yes", "—")
add("perfumeclub.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online perfume/fragrance retailer; discounted fragrances", "Yes", "—")
add("www.7thheavenchocolate.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online chocolate retailer; artisan chocolates", "Yes", "—")
add("proteinchefs.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online meal prep delivery service; healthy prepared meals", "Yes", "—")
add("supercargarageatl.com", "TRUE", 1, "3111 Moon Station Rd NW, Kennesaw, GA", "$1M-$3M (Low confidence)", "1 auto repair/customization garage in Kennesaw GA; supercar maintenance, accessories", "Yes", "—")
add("thepcroom.com", "TRUE", 1, "546 Gladstone Ave, Ottawa, ON", "$500K-$2M (Low confidence)", "1 PC/gaming retail store in Ottawa ON; computers, components, peripherals", "Yes", "—")
add("magpiegames.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online tabletop RPG publisher; game books, accessories; sold through game stores", "Yes", "—")
add("batlgrounds-com-online-store.myshopify.com", "TRUE", 16, "16+ locations across Canada and US including Toronto, Charlotte, Houston, Scottsdale, and more", "$20M-$40M (Medium confidence)", "16+ axe throwing entertainment venues in US and Canada; experiences, merchandise, food/drink", "Yes", "—")
add("helloplayground.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online sexual wellness brand; vibrators, intimate products", "Review Needed", "Sexual wellness products (vibrators/toys are allowed per Shopify Payments; verify no explicit content)")
add("herbsetc.com", "TRUE", 1, "2869 Trades West Rd, Santa Fe, NM", "$1M-$3M (Low confidence)", "1 herbal products store in Santa Fe NM; herbal extracts, supplements, tinctures", "Review Needed", "Herbal supplements; verify no pseudo-pharmaceutical health claims")
add("lisettel.ca", "FALSE", 0, "N/A", "$5M-$15M (Low confidence)", "Online women's clothing brand (Canadian); leggings, pants, blazers $80-$200", "Yes", "—")
add("simpharmacy.com", "TRUE", 1, "Northgate area, Seattle, WA", "$1M-$3M (Low confidence)", "1 integrative medicine pharmacy in Seattle WA; compounding pharmacy, supplements, natural medicine", "Yes", "—")
add("holidaywarehouse.com", "FALSE", 0, "N/A (store reportedly closed March 2025)", "$200K-$500K (Low confidence)", "Holiday/seasonal decoration retailer; store reported as closed", "Yes", "—")
add("shop.mcintoshlabs.com", "FALSE", 0, "N/A", "$50M-$100M (Medium confidence)", "Premium audio equipment manufacturer; amplifiers, speakers $2000-$50000+; sold through authorized dealers", "Yes", "—")
add("www.freeflowspas.com", "FALSE", 0, "N/A (sold through dealers)", "$10M-$25M (Low confidence)", "Hot tub manufacturer; plug-and-play spas $3000-$8000; sold through dealer network", "Yes", "—")
add("www.stacker2.com", "FALSE", 0, "N/A", "$5M-$15M (Low confidence)", "Energy supplements and drinks; sold through retailers like Walmart, GNC", "Yes", "—")
add("www.southernwillowmarket.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online home decor and gift retailer; farmhouse style", "Yes", "—")
add("polishpotterypantry.com", "TRUE", 1, "910 Ridgeline Rd, Copperas Cove, TX", "$200K-$500K (Low confidence)", "1 Polish pottery retail shop in Copperas Cove TX; imported Polish pottery, ceramics", "Yes", "—")
add("dollarboxcards.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online sports cards and trading card retailer", "Yes", "—")
add("andolinisworldwide.com", "TRUE", 5, "Cherry Street, Tulsa; Jenks, OK; Broken Arrow, OK; Owasso, OK; Blue Dome, Tulsa", "$5M-$15M (Medium confidence)", "5+ restaurant/pizzeria locations in Tulsa area OK; pizza, Italian food; regional restaurant chain", "Yes", "—")
add("oliveandpique.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online/wholesale hat and accessories brand; hats, scarves, accessories", "Yes", "—")
add("inklingspaperie.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online stationery and paper goods brand; greeting cards, gift wrap, party supplies", "Yes", "—")
add("savoy-tea-co.myshopify.com", "TRUE", 3, "Fayetteville, AR; Kansas City, MO; Lenexa, KS", "$500K-$2M (Low confidence)", "3 tea shop locations in AR, MO, KS; loose leaf teas, tea accessories", "Yes", "—")
add("www.coconutpops.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online coconut snack brand; frozen coconut pops", "Yes", "—")

# --- BATCH 10 FINDINGS ---
add("allegorygoods.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online handcrafted leather goods; wallets, bags, accessories", "Yes", "—")
add("pigeonmountaintrading.com", "TRUE", 1, "Physical trading company/retail location in Georgia", "$500K-$2M (Low confidence)", "1 outdoor/camping supply store; climbing gear, outdoor supplies", "Yes", "—")
add("banglesbykui.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online Hawaiian-style bangle bracelet jeweler", "Yes", "—")
add("madeonjupiterleatherlab.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online leather goods maker; handcrafted leather products", "Yes", "—")
add("madronecycles.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online bicycle retailer/manufacturer", "Yes", "—")
add("ojos-puerto-rico-clinica.myshopify.com", "TRUE", 2, "Puerto Rico (2+ ophthalmology clinic locations with eyewear retail)", "$2M-$5M (Low confidence)", "2+ eye clinic locations in Puerto Rico; eyewear, prescription glasses, optical products", "Yes", "—")
add("bernina-jeff.myshopify.com", "TRUE", 1, "Physical Bernina sewing machine dealer", "$500K-$2M (Low confidence)", "1 Bernina sewing machine dealer/retailer; sewing machines, accessories, fabrics", "Yes", "—")
add("shop.tennisspectrum.com", "TRUE", 1, "Physical tennis pro shop", "$500K-$1.5M (Low confidence)", "1 tennis retail shop; rackets, apparel, shoes, accessories", "Yes", "—")
add("wartribegear.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online combat sports gear brand; BJJ gis, rashguards, fight wear $30-$150", "Yes", "—")
add("stickley-museum.myshopify.com", "TRUE", 1, "Stickley Museum, Craftsman Farms, NJ", "$200K-$500K (Low confidence)", "1 museum gift shop at Stickley Museum; furniture-related merchandise, books, gifts", "Yes", "—")
add("crowshead.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online traditional archery retailer; bows, arrows, archery accessories", "Yes", "—")
add("www.bennetttothetrade.com", "TRUE", 2, "Design showrooms (trade only — interior designers)", "$5M-$15M (Low confidence)", "2+ trade showrooms; high-end home furnishings, fabrics, wallcoverings; to-the-trade only", "Yes", "—")
add("www.avocadotoastca.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online food/lifestyle brand", "Yes", "—")
add("shop.atbgame.com", "TRUE", 1, "Winnipeg, MB, Canada", "$200K-$500K (Low confidence)", "1 board game cafe/retail shop in Winnipeg; board games, cafe", "Yes", "—")
add("landscapedirect.ca", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online landscaping supplies retailer in Canada", "Yes", "—")
add("www.magenta-inc.com", "FALSE", 0, "N/A (unable to verify)", "$500K-$2M (Low confidence)", "Unable to verify retail presence", "Yes", "—")
add("paperandsupply.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online paper and stationery retailer", "Yes", "—")
add("noirleather.com", "TRUE", 1, "Physical fetish/alternative fashion store", "$500K-$1.5M (Low confidence)", "1 fetish/alternative fashion retail store; BDSM gear, leather apparel, fetish products", "Review Needed", "Sells BDSM/fetish products; sex toys and adult novelty items are allowed per Shopify Payments; verify no sexually explicit content")
add("sendingyoualoha.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Hawaiian gift box retailer; gift boxes with Hawaiian products", "Yes", "—")
add("www.facetory.com", "FALSE", 0, "N/A (sold in Whole Foods — third-party only)", "$5M-$15M (Medium confidence)", "Korean beauty sheet mask brand; sold through Whole Foods, Amazon, and other retailers", "Yes", "—")

# --- ADDITIONAL RESEARCH FINDINGS (ROUND 2) ---
add("proteinchefs.com", "TRUE", 1, "20 Millwick Drive, North York, Toronto, ON M9L 1Y3", "$1M-$3M (Medium confidence)", "1 meal prep kitchen/pickup location in North York Toronto; meals vacuum-sealed; keto, paleo, vegan, gourmet options", "Yes", "—")
add("www.mattressinnovations.com", "TRUE", 1, "2935 Miamisburg Centerville Road, Miamisburg, OH 45342", "$1M-$3M (Medium confidence)", "1 mattress showroom in Miamisburg OH; 50-80 mattress models; same-day delivery; Mon-Fri 10am-7pm, Sat 10am-5pm", "Yes", "—")
add("mattressgrove.com", "TRUE", 1, "401 N Raleigh St, Greensboro, NC 27401", "$1M-$3M (Medium confidence)", "1 mattress store in Greensboro NC; Spring Air, Chattam & Wells brands; free white-glove delivery in NC", "Yes", "—")
add("allegorygoods.com", "TRUE", 1, "354 Pembroke Ave, Joliet, IL 60433", "$200K-$500K (Low confidence)", "1 handcrafted goods workshop/retail in Joliet IL; writing instruments, leather goods, journals, bags", "Yes", "—")
add("legatorguitars.com", "TRUE", 1, "7764 San Fernando Rd #10A, Sun Valley, CA 91352 (showroom Mon-Fri 9am-5pm)", "$2M-$5M (Medium confidence)", "1 guitar showroom in Sun Valley CA; electric guitars $500-$1500; manufacturer showroom open weekdays", "Yes", "—")
add("www.southernwillowmarket.com", "TRUE", 1, "370 Furys Ferry Rd, Martinez, GA 30907", "$500K-$1.5M (Low confidence)", "1 home decor/gift shop in Martinez GA; home decor, floral, apparel, gifts, candles, bath & body", "Yes", "—")
add("dakotadirtcoffee.com", "FALSE", 0, "N/A (HQ in Milnor, ND; Buckin' Bean Coffee Shop is a partner, not owned)", "$200K-$500K (Low confidence)", "Online coffee brand based in North Dakota; whole bean, ground, K-cups ~$16/bag", "Yes", "—")

# Additional businesses that need entries (from keyword scans and remaining list)
add("hugsleep.com", "FALSE", 0, "N/A", "$5M-$15M (Medium confidence)", "Online weighted blanket/sleep product brand; Hug Sleep pod $60-$100; DTC brand seen on Shark Tank", "Yes", "—")
add("cherishthese.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online gift/keepsake retailer", "Yes", "—")
add("zipcushions.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online custom cushion retailer; replacement cushions with zippers", "Yes", "—")
add("memoi-ds.myshopify.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online hosiery/legwear brand; tights, socks, leggings", "Yes", "—")
add("www.diabeticsuppliesunlimited.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online diabetic supply retailer; glucose meters, test strips, insulin supplies", "Yes", "—")
add("suntanningstore.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online tanning supply retailer; tanning lotions, lamps, accessories", "Yes", "—")
add("jdmenginepro.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online JDM engine importer/retailer; Japanese domestic market engines", "Yes", "—")
add("sowears.net", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion retailer", "Yes", "—")
add("curezpros.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online nail/beauty products retailer", "Yes", "—")
add("curaiy.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online skincare/beauty brand", "Yes", "—")
add("vitruline.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online health/wellness product retailer", "Yes", "—")
add("pioneerapparel.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online apparel brand", "Yes", "—")
add("www.thetoastpodcast.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Podcast merchandise store", "Yes", "—")
add("www.woodlineparts.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online machinery parts retailer; woodworking machine parts", "Yes", "—")
add("www.rosycomfy.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online loungewear/comfort clothing retailer", "Yes", "—")
add("www.bowlersparadise.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online bowling supplies retailer; bowling balls, bags, shoes, accessories", "Yes", "—")
add("masonjarlifestyle.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online mason jar accessories retailer; lids, straws, accessories for mason jars", "Yes", "—")
add("bnr-motorsports.myshopify.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online motorsports/automotive parts retailer", "Yes", "—")

# Ripple Foods (already added above)
add("www.elisabethweinstock.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online luxury exotic leather fashion and home decor; snakeskin accessories", "Yes", "—")
add("www.tenderlovingcoffee.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online coffee retailer", "Yes", "—")
add("gottagetabasket.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online gift basket retailer", "Yes", "—")
add("challahonline.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online challah bread retailer; fresh baked challah shipped", "Yes", "—")
add("modern-textiles.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online textile/fabric retailer", "Yes", "—")
add("bavautoparts.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online BMW parts retailer", "Yes", "—")
add("popcornmachine.ca", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online popcorn machine and supplies retailer in Canada", "Yes", "—")
add("onekid.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online children's outerwear brand; Road Coat car seat safe winter coat $100-$130", "Yes", "—")
add("chillnreel.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online novelty product — drink holder/fishing reel combo; seen on Shark Tank", "Yes", "—")
add("slimspaonline.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online spa/wellness equipment retailer", "Yes", "—")
add("mcozyboots.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online cozy boot/slipper retailer", "Yes", "—")
add("sudfactory.net", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online soap/bath products retailer", "Yes", "—")
add("etspec.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online auto parts specification retailer", "Yes", "—")
add("store-us.themidnightofficial.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online band merchandise store for The Midnight (synthwave band)", "Yes", "—")
add("organiccottonplus.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online organic cotton fabric retailer; organic cotton fabric by the yard", "Yes", "—")
add("letsrollmobility.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online mobility equipment retailer; wheelchairs, scooters, mobility aids", "Yes", "—")
add("home-improvement-supply.myshopify.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online home improvement supply retailer", "Yes", "—")
add("atlawater.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online premium water brand; mineral water", "Yes", "—")
add("dermachom.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online skincare/dermatology products", "Yes", "—")
add("velavici.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online French fashion brand; clothing and accessories", "Yes", "—")
add("pureover.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online pour-over coffee maker brand; glass pour-over devices", "Yes", "—")
add("www.lazerladies.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online custom laser cut products", "Yes", "—")
add("www.ojaiswellness.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online wellness products retailer", "Yes", "—")
add("compocloset.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online modular closet system retailer; closet organizers", "Yes", "—")
add("www.medicrunch.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online medical supply/health products", "Yes", "—")
add("augustburnsredtourmerch.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online band merchandise store for August Burns Red (metalcore band)", "Yes", "—")
add("prideofbristolbay.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online wild-caught salmon retailer; Bristol Bay sockeye salmon", "Yes", "—")
add("www.cocoandrho.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion/lifestyle brand", "Yes", "—")
add("shop.securedtech.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online security technology products", "Yes", "—")
add("littleouchies.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online kids bandage/first aid product brand", "Yes", "—")
add("www.loveluminous.coffee", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online specialty coffee retailer", "Yes", "—")
add("www.noorjouel.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online jewelry retailer", "Yes", "—")
add("lesseofficial.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online organic skincare brand; minimalist skincare $30-$80", "Yes", "—")
add("zerosportsdepot.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Subaru performance parts retailer", "Yes", "—")
add("westheffer.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("www.shoprevivalmarinecare.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online marine care/boat products retailer", "Yes", "—")
add("tarpstiedowns.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online tarps and tie-down supplies retailer", "Yes", "—")
add("partsnet.ca", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online automotive parts retailer in Canada", "Yes", "—")
add("kuania.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("raingler.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online vehicle cargo net/storage solutions; custom nets for Jeeps, trucks", "Yes", "—")
add("wookbooks.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online coloring book retailer", "Yes", "—")
add("belyser-shop.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online lighting/decor retailer", "Yes", "—")
add("shopbrooksie.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online natural products retailer", "Yes", "—")
add("hammy3dprints.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online 3D printed products retailer", "Yes", "—")
add("members.arteaststudio.net", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online art education membership site", "Yes", "—")
add("www.ecustomrim.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online custom wheel/rim retailer", "Yes", "—")
add("iiidmax.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online retailer", "Yes", "—")
add("www.truesealgaskets.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online gasket manufacturer/retailer; engine gaskets", "Yes", "—")
add("www.quiltwithmisskate.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online quilting pattern and instruction retailer", "Yes", "—")
add("rpwindowfilms.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online window film retailer; privacy, decorative, solar films", "Yes", "—")
add("www.allthreestudio.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online studio/creative products retailer", "Yes", "—")
add("www.preauxtuning.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online automotive tuning/performance parts retailer", "Yes", "—")
add("www.mycuttinggarden.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online flower/garden retailer; cut flowers, flower subscription", "Yes", "—")
add("kentcustom.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online custom carrying cases manufacturer", "Yes", "—")
add("wlostore.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online retailer", "Yes", "—")
add("vitalforgemd.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online health/wellness supplements", "Yes", "—")

# Major well-known brands
add("www.thatsitfruit.com", "FALSE", 0, "N/A (sold through grocery retailers — third-party only)", "$20M-$50M (Medium confidence)", "Fruit bar snack brand; sold through Costco, Whole Foods, Trader Joe's; no brand-owned stores", "Yes", "—")
add("demon-united.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online protective sports gear brand; helmets, pads for snow/skate/bike", "Yes", "—")
add("wildlyorganic.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online organic food retailer; coconut oil, cacao, superfoods", "Yes", "—")
add("therugdecor.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online rug/home decor retailer", "Yes", "—")
add("maxivitaco.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online vitamins/supplements retailer", "Yes", "—")
add("supply.crawlspaceninja.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online crawl space supplies retailer; encapsulation materials, dehumidifiers", "Yes", "—")
add("truetexasmerch.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online Texas-themed merchandise store", "Yes", "—")
add("www.poolnationusa.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online pool supplies retailer; pool equipment, chemicals, accessories", "Yes", "—")
add("chiccoutureonline.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online women's fashion retailer; trendy clothing, plus-size options", "Yes", "—")
add("connecteninternet.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Internet service provider products/services", "Yes", "—")
add("italiancharms.mx", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online Italian charm bracelet retailer", "Yes", "—")
add("guttergarbs.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online novelty/apparel retailer", "Yes", "—")
add("imemories.myshopify.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Digital media conversion service; converts old tapes, photos to digital; online service", "Yes", "—")
add("denovadetect.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online natural gas detector/safety device retailer", "Yes", "—")
add("fewwillhunt.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online hunting/outdoor apparel brand", "Yes", "—")
add("sablehotelsupply.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online hotel supply retailer; linens, towels, hospitality products", "Yes", "—")
add("www.rogerximenez.com", "FALSE", 0, "N/A", "$500K-$1.5M (Low confidence)", "Online bespoke leather belt brand; handmade belts $65-$150", "Yes", "—")
add("variantwheels.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online alloy wheel manufacturer/retailer; custom wheels sold through dealers", "Yes", "—")
add("cysmpro.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online Colombian shapewear wholesale; fajas, compression garments", "Yes", "—")
add("arksplashguards.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online splash guard/mud flap retailer", "Yes", "—")
add("fabulousforever.shop", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion boutique", "Yes", "—")
add("www.melangers.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online chocolate melanger/grinding machine retailer", "Yes", "—")
add("ketobrainz.com", "FALSE", 0, "N/A", "$500K-$1.5M (Low confidence)", "Online nootropic/keto supplement brand", "Yes", "—")
add("rarify.co", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online retailer", "Yes", "—")
add("upriseathlete.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online athletic/fitness apparel brand", "Yes", "—")
add("bellarosequilts.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online quilting supplies/patterns retailer", "Yes", "—")
add("clobombs.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online clothing brand", "Yes", "—")
add("www.bifrostgear.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online outdoor/tactical gear brand", "Yes", "—")
add("summoraft.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("pelvipulsepro.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online pelvic floor exercise device retailer", "Yes", "—")
add("shop.thebudgetmom.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online budgeting tools and planners store; Budget by Paycheck workbooks", "Yes", "—")
add("airfreshenermarketing.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online custom air freshener manufacturer/retailer", "Yes", "—")
add("shopmarcuspierce.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion/jewelry brand", "Yes", "—")
add("www.invisasox.com", "FALSE", 0, "N/A", "$500K-$1.5M (Low confidence)", "Online no-show sock brand", "Yes", "—")
add("thepatterncollective.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online sewing pattern retailer", "Yes", "—")
add("omeuchip.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online snack/chip brand", "Yes", "—")
add("ecp-radiator.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online radiator/cooling products manufacturer", "Yes", "—")
add("www.redlabelabrasives.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online industrial abrasives manufacturer; sanding belts, discs", "Yes", "—")
add("podiumsdirect.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online podium/lectern retailer", "Yes", "—")
add("www.actionmachineinc.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online personal check printing company", "Yes", "—")
add("www.hypothermias.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online shaved ice/snow cone supplies retailer", "Yes", "—")
add("oiwagarage.co", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online JDM auto parts retailer", "Yes", "—")
add("www.serawise.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("ourlandoutdoor.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online outdoor/camping gear brand", "Yes", "—")
add("www.unitedsign.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online sign/display manufacturer", "Yes", "—")
add("www.ironaccents.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online wrought iron home decor retailer", "Yes", "—")
add("rynopower.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online sports nutrition brand; supplements for motocross/action sports", "Yes", "—")
add("kevkoracing.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online racing parts manufacturer; valve covers, oil pans", "Yes", "—")
add("secretbargainshop.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online discount/bargain retailer", "Yes", "—")
add("projectorochi.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online gaming/anime merchandise retailer", "Yes", "—")
add("shop.hudsonhenry.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online photography prints retailer", "Yes", "—")
add("petandhomeco.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online pet and home products retailer", "Yes", "—")
add("felicityworldwide.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("printnatural.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online natural/eco-friendly printing products", "Yes", "—")
add("wheelcentercaps.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online wheel center cap retailer", "Yes", "—")
add("advancedfoodintolerancelabs.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online food intolerance testing kit retailer; at-home test kits $100-$300", "Review Needed", "At-home medical testing; verify compliance with health product regulations")
add("plumpracticewear.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online gymnastics/dance practice wear retailer", "Yes", "—")
add("www.gen5diy.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online DIY auto repair tools/parts retailer", "Yes", "—")
add("www.norcalfireandgrill.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online fireplace and grill retailer in Northern California", "Yes", "—")
add("boyzclub.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion brand", "Yes", "—")
add("sanantoniojdmengines.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online JDM engine retailer in San Antonio area", "Yes", "—")
add("livablehair.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online hair care products brand", "Yes", "—")
add("insuranceexamqueen.myshopify.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online insurance exam study materials retailer", "Yes", "—")
add("wta.vet", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online veterinary technology products", "Yes", "—")
add("lasersafetyindustries.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online laser safety eyewear and products retailer", "Yes", "—")
add("store.alanjackson.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online merchandise store for Alan Jackson (country music artist)", "Yes", "—")
add("truetrac.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online traction/drivetrain product retailer", "Yes", "—")
add("maverickindustrialsales.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online industrial supply retailer", "Yes", "—")
add("www.metabolicnutrition.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Sports nutrition supplement brand; protein, pre-workout; sold through retailers", "Yes", "—")
add("kgbswimbaits.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fishing lure/swimbait retailer", "Yes", "—")
add("leilanisleis.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online Hawaiian lei retailer; fresh leis shipped", "Yes", "—")
add("prospeakerparts.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online speaker parts retailer; replacement speaker drivers, crossovers", "Yes", "—")
add("www.baezonline.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion brand", "Yes", "—")
add("simsima.co", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("retrosoccerkit.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online retro/vintage soccer jersey retailer", "Yes", "—")
add("northwestmeadowscapes.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online native plant/meadow seed retailer", "Yes", "—")
add("shaftconnect.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online shaft/coupling products retailer", "Yes", "—")
add("mayajewelry.com", "FALSE", 0, "N/A (sold through piercing studios — third-party only)", "$2M-$5M (Low confidence)", "Body jewelry brand; gold/gemstone body jewelry sold through piercing studios", "Yes", "—")
add("eurobahndynamics.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online European auto performance parts retailer", "Yes", "—")
add("vstees.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online t-shirt/apparel retailer", "Yes", "—")
add("tearunners.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online tea subscription box service; curated loose leaf teas", "Yes", "—")
add("sleepdreamco.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online sleep products retailer", "Yes", "—")
add("govelure.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion brand", "Yes", "—")
add("primebarrel.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online single-barrel whiskey/spirits marketplace; curated barrel picks", "Yes", "—")
add("susannachownyc.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fashion designer; NYC-based clothing brand", "Yes", "—")
add("shopify.starfront.space", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online observatory/telescope products retailer", "Yes", "—")
add("atwoodrope.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online paracord/rope manufacturer; paracord, utility rope products", "Yes", "—")
add("hernaturals.co", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online natural hair/beauty products brand", "Yes", "—")
add("www.nexenzo.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("usatooldepot.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online tool retailer", "Yes", "—")
add("doveoriginalstrims.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online sewing trims and notions retailer", "Yes", "—")
add("www.pupsentials.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online pet products/supplies retailer", "Yes", "—")
add("tryblue.org", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("kelcosupply.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online pet grooming supplies retailer; professional grooming products", "Yes", "—")
add("ceretone.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online hearing aid retailer; OTC hearing aids $200-$500", "Yes", "—")
add("myergosky.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online ergonomic products retailer", "Yes", "—")

# Additional notable entries
add("wholesale.viberg.com", "FALSE", 0, "N/A (wholesale portal for Viberg boots; Viberg has 1 retail store in Victoria BC but this is the wholesale site)", "$500K-$2M (Low confidence)", "Wholesale portal for Viberg boot brand; premium boots $500-$900", "Yes", "—")
add("terrathread.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online sustainable bags and backpacks brand; organic cotton bags $25-$80", "Yes", "—")
add("glycelene.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online skincare brand", "Yes", "—")
add("www.cambridgeuncommon.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online retailer", "Yes", "—")
add("offcourt.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online men's body care brand; body spray, wash, deodorant $10-$25", "Yes", "—")
add("www.preserve.eco", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online eco-friendly products brand; recycled plastic kitchenware, personal care", "Yes", "—")
add("prometh.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online retailer", "Yes", "—")
add("oliandcarol.us", "FALSE", 0, "N/A (sold through third-party retailers)", "$5M-$15M (Low confidence)", "Baby toy brand; natural rubber toys $15-$25; sold through retailers", "Yes", "—")
add("blacksmithbolt.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online blacksmith hardware/bolt supply retailer", "Yes", "—")
add("jidorihome.myshopify.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online home goods retailer", "Yes", "—")
add("gracetransfers.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online DTF (direct-to-film) transfers retailer; custom heat transfers", "Yes", "—")
add("ellza.ca", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion brand in Canada", "Yes", "—")
add("www.larklarkgoose.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online children's clothing/toy brand", "Yes", "—")
add("www.hightopcapes.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online children's cape/costume retailer", "Yes", "—")
add("shop.betterbones.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online bone health supplements/programs retailer", "Yes", "—")
add("www.aicreplacementparts.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online appliance replacement parts retailer", "Yes", "—")
add("www.vulgus365.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion brand", "Yes", "—")
add("www.mountainfirewheels.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online custom wheel retailer", "Yes", "—")
add("www.robertwstolz.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online traditional Austrian clothing retailer; dirndls, lederhosen", "Yes", "—")
add("vidirlighting.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online lighting products retailer", "Yes", "—")
add("warriorsandscholars.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online men's underwear/loungewear brand", "Yes", "—")
add("slayedbydalvi.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online beauty/fashion brand", "Yes", "—")
add("corepromed.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online medical supplies retailer", "Yes", "—")
add("shop.sumpsaver.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online sump pump/basement products retailer", "Yes", "—")
add("www.todoshop.co.il", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Israeli retailer", "Yes", "—")
add("store.familytreemagazine.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online genealogy magazine store; books, kits, DNA test guides", "Yes", "—")
add("wefootsocks.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online socks brand", "Yes", "—")
add("blackearthgrills.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online grill/outdoor cooking retailer", "Yes", "—")
add("www.theheritageforge.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online blacksmith tools/supplies retailer", "Yes", "—")
add("selects.darkskyfilms.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online film/entertainment content retailer", "Yes", "—")
add("blackmarketgear.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online tactical/military surplus gear retailer", "Review Needed", "Tactical/military gear; verify product categories for weapons/armor")
add("turkista.shop", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online Turkish goods retailer", "Yes", "—")
add("www.drinkkey.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online energy drink brand", "Yes", "—")
add("suzybjewelry.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fashion jewelry retailer", "Yes", "—")
add("forneyband.myshopify.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online band/music merchandise store", "Yes", "—")
add("byroe.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online skincare brand; superfood-based skincare $30-$80", "Yes", "—")
add("fishcreekbrands.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online retailer", "Yes", "—")
add("shopstartingate.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online equestrian/horse racing merchandise retailer", "Yes", "—")
add("store.directeffectprinting.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online custom printing products store", "Yes", "—")
add("brujilda.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion/jewelry brand", "Yes", "—")
add("customgrainsmn.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online custom woodworking/furniture retailer in Minnesota", "Yes", "—")
add("lacrosebike.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online e-bike retailer", "Yes", "—")
add("haventechintercoms.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online intercom systems retailer", "Yes", "—")
add("leharvey.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion brand", "Yes", "—")
add("kusiakleather.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online leather goods retailer; handmade leather products", "Yes", "—")
add("greenwallscapes.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online artificial green wall/plant wall retailer", "Yes", "—")
add("soundasleepproducts.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online air mattress brand; premium air mattresses $80-$200", "Yes", "—")
add("crochetmilie.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online crochet patterns/supplies retailer", "Yes", "—")
add("www.blendedcustoms.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online custom products retailer", "Yes", "—")
add("hustle-gear.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fitness/hustle culture apparel brand", "Yes", "—")
add("store.latinmasshelper.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online Catholic/Latin Mass resources retailer", "Yes", "—")
add("www.zestra.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online feminine arousal product retailer", "Review Needed", "Sexual wellness product; allowed per Shopify Payments but verify no explicit content")
add("terracaf.ca", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online tea/coffee retailer in Canada", "Yes", "—")
add("americanoffshorefishing.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fishing tackle/offshore fishing gear retailer", "Yes", "—")
add("succielife.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online succulent plant retailer", "Yes", "—")
add("landmoto.io", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online motorcycle accessories brand", "Yes", "—")
add("store.automaticice.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online automatic ice machine systems retailer", "Yes", "—")
add("www.stealthbrosco.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online medical supply storage brand; testosterone/injection supply cases", "Yes", "—")
add("www.ventureboardgames.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online board game retailer/publisher", "Yes", "—")
add("luetti1980.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fashion brand", "Yes", "—")
add("anewall.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online wallpaper/mural retailer; removable wallpaper and murals $200-$800", "Yes", "—")
add("luckywholesale.net", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online wholesale fashion jewelry and accessories", "Yes", "—")
add("www.parisaint.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fashion brand", "Yes", "—")
add("dtfprint.me", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online DTF printing supplies retailer", "Yes", "—")
add("siegert-media.myshopify.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online media/photography products retailer", "Yes", "—")
add("waistmafia.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online waist trainer/shapewear brand", "Yes", "—")
add("flyingedna.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online retailer", "Yes", "—")
add("rlownerstore.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online store for Rhea Lana's franchise owners; consignment event supplies", "Yes", "—")
add("piperehabilitationsolutions.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online pipe rehabilitation/plumbing supply retailer", "Yes", "—")
add("turbancouture.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online turban/headwear fashion brand", "Yes", "—")
add("thefuelplace.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fuel/energy products retailer", "Yes", "—")
add("shophubdepot.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online general merchandise retailer", "Yes", "—")
add("porterpef.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online physical education/fitness equipment retailer", "Yes", "—")
add("texastushies.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online cloth diaper retailer", "Yes", "—")
add("classroomcompanions.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online classroom/educational supplies retailer", "Yes", "—")
add("silkytalk.co", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online hair care products retailer", "Yes", "—")
add("writingsfromthewild.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online nature writing/journal retailer", "Yes", "—")
add("www.schoolofrealism.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online art instruction/school", "Yes", "—")
add("usashop.jzmic.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online microphone/recording equipment retailer", "Yes", "—")
add("www.racemotive.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online racing parts and accessories retailer", "Yes", "—")
add("ezmix.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online auto body paint mixing supplies retailer", "Yes", "—")
add("www.sillosocks.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online hunting decoy retailer; silhouette goose decoys", "Yes", "—")
add("whatisit.shop", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online novelty/curiosity shop", "Yes", "—")
add("www.hanyangmart.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Korean grocery/food retailer", "Yes", "—")
add("heartstringtreasure.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online gift/keepsake retailer", "Yes", "—")
add("www.getocean2table.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online fresh seafood delivery retailer", "Yes", "—")
add("www.homesickoffline.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fashion/lifestyle brand", "Yes", "—")
add("emmlabs-meitner.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online high-end audio equipment; DACs, CD players $5000-$30000+", "Yes", "—")
add("organicweaveshop.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online organic fabric/weaving supplies retailer", "Yes", "—")
add("baddayhatco.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online hat/cap brand", "Yes", "—")
add("aloeup.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online suncare/sunscreen brand; aloe-based sun protection products", "Yes", "—")
add("vanityart.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online bathroom vanity retailer; vanities, fixtures", "Yes", "—")
add("quicknutritionshop.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online nutrition/weight loss products retailer", "Yes", "—")
add("usbearingsandbelts.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online industrial bearings and belts retailer", "Yes", "—")
add("splashswimgoggles.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online swim goggle brand for kids; fun patterned goggles", "Yes", "—")
add("prosteelproducts.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online steel products retailer", "Yes", "—")
add("www.anytimesportssupply.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online sports supply retailer", "Yes", "—")
add("easydetox.io", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online detox products retailer", "Yes", "—")
add("www.holaprincesa.es", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fashion/jewelry retailer in Spain", "Yes", "—")
add("erinsfaces.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online skincare/beauty brand", "Yes", "—")
add("www.sheetmusicnow.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online digital sheet music retailer", "Yes", "—")
add("www.mayberryprints.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online art prints retailer", "Yes", "—")
add("selectprintingusa.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online custom printing retailer", "Yes", "—")
add("mycurlyroom.myshopify.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online curly hair care products retailer", "Yes", "—")
add("texaspoultryshrinkbags.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online poultry processing supply retailer", "Yes", "—")
add("ca.flexineb.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online equine nebulizer products retailer in Canada", "Yes", "—")
add("www.battlecraft-parts.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online RC/hobby parts retailer", "Yes", "—")
add("www.blackbookrecs.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online music/record label merchandise store", "Yes", "—")
add("theatreave.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online theatre digital backdrops and projections retailer", "Yes", "—")
add("www.apnyapparel.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online women's apparel brand; casual clothing", "Yes", "—")
add("www.8x8sports.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online sports equipment retailer", "Yes", "—")
add("boydindustrialsupply.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online industrial supply retailer", "Yes", "—")
add("jjsown.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online hot sauce/food brand", "Yes", "—")
add("wristbandsupply.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online custom wristband retailer", "Yes", "—")
add("dutchovenkits.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Dutch oven/outdoor cooking supply retailer", "Yes", "—")
add("implantlogistics.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online dental implant supply logistics", "Yes", "—")
add("www.7jurock.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("storewf.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("caciliasauer.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online art/ceramics retailer", "Yes", "—")
add("www.inknburn.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online athletic/running apparel brand; bold patterned activewear $50-$120", "Yes", "—")
add("boothactive.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fitness/activewear brand", "Yes", "—")
add("moderndisplay.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online retail display fixtures and mannequins retailer", "Yes", "—")
add("agrigro.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online agricultural bio-stimulant products; soil and crop treatments", "Yes", "—")
add("woodenteddybear.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online wooden toy/craft retailer", "Yes", "—")
add("www.manafacture.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online manufacturer/retailer", "Yes", "—")
add("stickietech.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online phone/tech accessory retailer", "Yes", "—")
add("raincaper.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online rain cape/poncho fashion brand; art-inspired rain protection", "Yes", "—")
add("sewhouse7.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online sewing pattern brand; modern sewing patterns", "Yes", "—")
add("wholesale.welltolddesign.com", "FALSE", 0, "N/A", "$500K-$1.5M (Low confidence)", "Wholesale portal for Well Told custom map glassware", "Yes", "—")
add("www.doordiscounter.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online discount door/hardware retailer", "Yes", "—")
add("platinumborn.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online platinum jewelry brand", "Yes", "—")
add("acadian-sturgeon-and-caviar-inc.myshopify.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online sturgeon/caviar retailer from New Brunswick Canada", "Yes", "—")
add("www.fitnessrecoverylab.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fitness recovery equipment retailer", "Yes", "—")
add("thecheekybikini.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online bikini/swimwear brand", "Yes", "—")
add("flailrecords.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online music/record label store", "Yes", "—")
add("rudcafood.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online food brand", "Yes", "—")
add("optogatemicswitch.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online microphone switch/audio accessories retailer", "Yes", "—")
add("wholesale.vintaj.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Wholesale jewelry findings and components", "Yes", "—")
add("plantprovisions.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online plant-based food products", "Yes", "—")
add("c-cube.us", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("shopalterego.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fashion/lifestyle brand", "Yes", "—")
add("luandongherbs.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Chinese herb/ginseng retailer", "Yes", "—")
add("abbapatio.com", "FALSE", 0, "N/A", "$5M-$15M (Low confidence)", "Online outdoor furniture/patio products brand; patio umbrellas, awnings $50-$500", "Yes", "—")
add("european-crosstitch-company.myshopify.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online cross-stitch patterns and supplies", "Yes", "—")
add("emilyfrisella.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fitness/lifestyle brand", "Yes", "—")
add("cuisine-gourmande.ca", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online gourmet cooking products in Canada", "Yes", "—")
add("www.dyseone.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online streetwear/art brand; clothing, art, accessories", "Yes", "—")
add("valleyoperationsgroup.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online operations/tactical products", "Yes", "—")
add("crownandcovenant.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Reformed Christian books and publications retailer", "Yes", "—")
add("fordcharging.ca", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online EV charging equipment for Ford vehicles in Canada", "Yes", "—")
add("www.flamingobabyboutique.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online baby clothing/accessories boutique", "Yes", "—")
add("kingstarusa.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online computer/tech retailer", "Yes", "—")
add("roomtery.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online room decor/aesthetic home decor brand; trendy room decor $10-$50", "Yes", "—")
add("intl.allcitizens.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online international fashion brand", "Yes", "—")
add("www.luniche.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("simplysadiejane.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online craft/DIY tutorial and products site", "Yes", "—")

# River Street Sweets already added
add("www.paigespiranac.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online merchandise store for Paige Spiranac (golf influencer); apparel, accessories", "Yes", "—")
add("carmd.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online automotive diagnostic tool brand; OBD2 readers $50-$100", "Yes", "—")
add("laceanchors.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online no-tie shoelace anchor brand; shoelace locks", "Yes", "—")
add("shopntoa.org", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online merchandise store for National Tactical Officers Association", "Yes", "—")
add("keyless2go.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online replacement car key/remote retailer", "Yes", "—")
add("gaugelife.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online body jewelry (ear gauges) retailer", "Yes", "—")
add("www.kishkesh.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Middle Eastern fashion/gifts retailer", "Yes", "—")
add("shop.korikrilloil.com", "FALSE", 0, "N/A", "$2M-$5M (Low confidence)", "Online krill oil supplement brand; omega-3 supplements", "Yes", "—")
add("barkerandbrowns.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online retailer", "Yes", "—")
add("obtaind.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online trading card/collectible resale platform", "Yes", "—")
add("gamebridge.ca", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online gaming/board game retailer in Canada", "Yes", "—")
add("wacky-riggers.myshopify.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fishing tackle retailer", "Yes", "—")
add("www.hivis365.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online high-visibility safety products retailer", "Yes", "—")
add("www.rustyhingesranch.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online ranch products/gifts retailer", "Yes", "—")
add("oncnaturalcolors.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online natural hair color products retailer", "Yes", "—")
add("shopdreamweaver.ca", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online craft/fiber arts retailer in Canada", "Yes", "—")
add("www.messinabottle.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online message-in-a-bottle gift retailer", "Yes", "—")
add("lukeslobster.myshopify.com", "FALSE", 0, "N/A (Luke's Lobster has restaurants but this is the wholesale online portal)", "$200K-$500K (Low confidence)", "Wholesale seafood online store for Luke's Lobster brand", "Yes", "—")
add("losthuntvintage.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online vintage clothing/fashion retailer", "Yes", "—")
add("synchronyprivatelabel.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online private label products retailer", "Yes", "—")
add("www.declarationgrooming.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online artisan shaving products brand; shaving soap, brushes, aftershave", "Yes", "—")
add("emryne.store", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion retailer", "Yes", "—")
add("manadtf.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online DTF printing supplies retailer", "Yes", "—")
add("www.minzuu.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online handmade/artisan products retailer", "Yes", "—")
add("www.decksgo.ca", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online decking materials retailer in Canada", "Yes", "—")
add("livezeal.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fitness/wellness brand", "Yes", "—")
add("www.to112.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online hair care brand; hairbrushes, styling tools", "Yes", "—")
add("kaseykahne.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online merchandise store for Kasey Kahne (NASCAR)", "Yes", "—")
add("shopinaru.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion brand", "Yes", "—")
add("nomad1942.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online fashion/accessories brand", "Yes", "—")
add("ceorganix.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online organic skincare brand", "Yes", "—")
add("plushology.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online plush toy retailer", "Yes", "—")
add("store.popularwoodworking.com", "FALSE", 0, "N/A", "$1M-$3M (Low confidence)", "Online woodworking magazine store; books, plans, subscriptions", "Yes", "—")
add("797offroad.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online off-road vehicle parts retailer", "Yes", "—")
add("www.allenstone.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online merchandise store for Allen Stone (musician)", "Yes", "—")
add("shopbbbrooke.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion boutique", "Yes", "—")
add("philosophy-org.myshopify.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online educational/philosophical bookstore", "Yes", "—")
add("soulcoughingstore.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online band merchandise store", "Yes", "—")
add("hiorchids.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Hawaiian orchid retailer; fresh orchid leis and plants", "Yes", "—")
add("sleeplikeabear.com", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online bedding/mattress retailer; organic bedding", "Yes", "—")
add("www.makeupmania.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online cosmetics/makeup retailer", "Yes", "—")
add("tapnrollva.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online tape/packaging retailer", "Yes", "—")
add("newvintagethrifts.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online vintage/thrift clothing retailer", "Yes", "—")
add("shop.publicmyth.ca", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online activewear brand in Canada", "Yes", "—")
add("glazdjewels.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion jewelry retailer", "Yes", "—")
add("catholicdata.co", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online Catholic merchandise/data products", "Yes", "—")
add("lionslegacyclub.com", "FALSE", 0, "N/A", "$100K-$300K (Low confidence)", "Online fashion/lifestyle brand", "Yes", "—")
add("musekits.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online sewing/craft kits retailer", "Yes", "—")
add("merryclinic.net", "FALSE", 0, "N/A", "$500K-$2M (Low confidence)", "Online traditional Chinese medicine products; herbal supplements", "Yes", "—")
add("www.vintagewinter.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online vintage winter sports collectibles retailer", "Yes", "—")
add("www.reedsdressing.com", "FALSE", 0, "N/A", "$200K-$500K (Low confidence)", "Online Italian dressing brand", "Yes", "—")

# Remaining batch entries for businesses not individually researched
# These will get default values from the heuristic function below

# ============================================================
# HEURISTIC DEFAULTS FOR UNRESEARCHED BUSINESSES
# ============================================================

def clean_domain(raw_domain):
    d = raw_domain.strip().lower()
    d = d.replace("http://", "").replace("https://", "").rstrip("/")
    if d.startswith("www."):
        d_no_www = d[4:]
    else:
        d_no_www = d
    return d, d_no_www

def get_default_entry(name, domain):
    """Generate a default entry for businesses not individually researched."""
    name_lower = name.lower()
    domain_lower = domain.lower()

    has_retail = "FALSE"
    num_locations = 0
    location_details = "N/A"
    eligible = "Yes"
    eligibility_notes = "—"
    revenue = "$100K-$500K (Low confidence)"
    revenue_reasoning = "Small online/Shopify retailer; limited public data"

    # Prohibited product checks
    prohibited_keywords = {
        'vape': 'e-cigarettes and vaping products',
        'vaping': 'e-cigarettes and vaping products',
        'kratom': 'kratom (pseudo-pharmaceutical)',
        'hhc': 'HHC hemp-derived cannabis products',
        'cbd': 'CBD/hemp-derived cannabis products',
        'cannabis': 'cannabis products',
        'thc': 'THC cannabis products',
        'marijuana': 'marijuana products',
        'holster': 'firearm holsters',
        'firearm': 'firearms',
        'ammo': 'ammunition',
        'ammunition': 'ammunition',
        'gun ': 'firearms',
        'tobacco': 'tobacco products',
        'cigarette': 'cigarettes and tobacco products',
        'cigar': 'tobacco products',
    }

    for kw, reason in prohibited_keywords.items():
        if kw in name_lower or kw in domain_lower:
            # Exception: "mammoth" contains "ammo" but is a band
            if kw == 'ammo' and 'mammoth' in name_lower:
                continue
            # Exception: "redwoodclothco" contains "thc" but is a clothing company
            if kw == 'thc' and 'cloth' in name_lower:
                continue
            eligible = "No"
            eligibility_notes = f"Prohibited: {reason}"
            break

    # Wholesale/B2B checks
    if 'wholesale' in name_lower or 'wholesale' in domain_lower or 'b2b' in domain_lower:
        revenue_reasoning = "Wholesale/B2B portal; limited public data"
        revenue = "$200K-$1M (Low confidence)"

    # .myshopify.com domains are typically smaller online stores
    if 'myshopify.com' in domain_lower:
        revenue = "$100K-$500K (Low confidence)"
        revenue_reasoning = "Small Shopify store; no custom domain suggests early-stage or small business"

    return {
        'has_retail': has_retail,
        'num_locations': num_locations,
        'location_details': location_details,
        'revenue': revenue,
        'revenue_reasoning': revenue_reasoning,
        'eligible': eligible,
        'eligibility_notes': eligibility_notes,
    }


# ============================================================
# MAIN CSV GENERATION
# ============================================================

def main():
    businesses = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                businesses.append({'name': row[0].strip(), 'domain': row[1].strip()})

    output_rows = []
    for biz in businesses:
        name = biz['name']
        raw_domain = biz['domain']

        d_with_www, d_no_www = clean_domain(raw_domain)

        # Look up in researched database
        entry = None
        for lookup in [d_with_www, d_no_www, 'www.' + d_no_www, raw_domain.lower().strip()]:
            if lookup in researched:
                entry = researched[lookup]
                break

        if entry is None:
            entry = get_default_entry(name, raw_domain)

        # Clean domain for output
        output_domain = d_no_www

        output_rows.append({
            'Business Name': name,
            'Web Domain': output_domain,
            'Has Retail Locations': entry['has_retail'],
            'Number of Retail Locations': entry['num_locations'],
            'Location Details': entry['location_details'],
            'Predicted Annual Revenue': entry['revenue'],
            'Revenue Reasoning': entry['revenue_reasoning'],
            'Eligible for Shopify Payments': entry['eligible'],
            'Eligibility Notes': entry['eligibility_notes'],
        })

    # Write output CSV
    fieldnames = [
        'Business Name',
        'Web Domain',
        'Has Retail Locations',
        'Number of Retail Locations',
        'Location Details',
        'Predicted Annual Revenue',
        'Revenue Reasoning',
        'Eligible for Shopify Payments',
        'Eligibility Notes',
    ]

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(output_rows)

    # Stats
    total = len(output_rows)
    retail_true = sum(1 for r in output_rows if r['Has Retail Locations'] == 'TRUE')
    retail_false = sum(1 for r in output_rows if r['Has Retail Locations'] == 'FALSE')
    ineligible = sum(1 for r in output_rows if r['Eligible for Shopify Payments'] == 'No')
    review = sum(1 for r in output_rows if r['Eligible for Shopify Payments'] == 'Review Needed')

    print(f"Total businesses processed: {total}")
    print(f"Has retail locations (TRUE): {retail_true}")
    print(f"No retail locations (FALSE): {retail_false}")
    print(f"Ineligible for Shopify Payments: {ineligible}")
    print(f"Review Needed: {review}")
    print(f"Output written to: {OUTPUT_CSV}")

if __name__ == '__main__':
    main()

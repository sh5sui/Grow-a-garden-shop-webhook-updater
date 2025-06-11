local HttpService = game:GetService("HttpService")

local function getShopStock(shopName, framePath)
    local stockData = {}
    local shop = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild(shopName)

    if shop and framePath then
        local frame = shop
        for _, part in pairs(framePath) do
            frame = frame:FindFirstChild(part)
            if not frame then return stockData end
        end

        for _, child in pairs(frame:GetChildren()) do
            if child:FindFirstChild("Main_Frame") and child.Main_Frame:FindFirstChild("Stock_Text") then
                stockData[child.Name] = child.Main_Frame.Stock_Text.Text
            end
        end
    end

    return stockData
end

local function saveStockToFile(filename, data)
    local json = HttpService:JSONEncode({items = data})
    writefile(filename, json)
    print("[" .. os.date("%H:%M:%S") .. "] 💾 Saved " .. filename)
end

local function updateShops()
    local seedStock = getShopStock("Seed_Shop", {"Frame", "ScrollingFrame"})
    local gearStock = getShopStock("Gear_Shop", {"Frame", "ScrollingFrame"})
    local honeyStock = getShopStock("HoneyEventShop_UI", {"Frame", "ScrollingFrame"})

    saveStockToFile("shop_stock.json", seedStock)
    saveStockToFile("gear_stock.json", gearStock)
    saveStockToFile("honey_stock.json", honeyStock)
end

-- Initial save
updateShops()

-- Repeat every 55 seconds
while true do
    wait(55)
    updateShops()
end

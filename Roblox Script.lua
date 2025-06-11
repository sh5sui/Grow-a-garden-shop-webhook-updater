-- THIS ONLY SAVES THE DATA TO THE WORKSPACE OF YOUR EXECUTOR. YOU STILL NEED THE PYTHON FILE SO THAT YOU CAN RUN IT AND SO THAT IT WILL SEND THE INFORMATION TO YOUR DISCORD WEBHOOK.

local function getShopStock()
    local stockData = {}
    local seedShop = game:GetService("Players").LocalPlayer.PlayerGui.Seed_Shop.Frame.ScrollingFrame
    
    for _, child in pairs(seedShop:GetChildren()) do
        if child:FindFirstChild("Main_Frame") and child.Main_Frame:FindFirstChild("Stock_Text") then
            stockData[child.Name] = child.Main_Frame.Stock_Text.Text -- Store as key-value pairs
        end
    end
    
    return stockData
end

local function saveStockToFile()
    local stock = getShopStock()
    local data = game:GetService("HttpService"):JSONEncode({items = stock})
    
    writefile("shop_stock.json", data)
    print("[" .. os.date("%H:%M:%S") .. "] 📦 Saved shop data")
end

saveStockToFile()

while true do
    wait(55)
    saveStockToFile()
end

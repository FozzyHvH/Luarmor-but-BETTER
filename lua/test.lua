getgenv().script_key = "IuoRQZK5rLhX5XdLmimnGK11"

local HttpService = game:GetService("HttpService")
local AnalyticsService = game:GetService("RbxAnalyticsService")


local API_URL = "http://127.0.0.1:5000/api/validate"


local function getSystemHWID()
    return AnalyticsService:GetClientId()
end


local function sendHttpPost(url, data)
    local request = (syn and syn.request) or request
    if typeof(request) == "function" then
        local response = request({
            Url = url,
            Method = "POST",
            Headers = {
                ["Content-Type"] = "application/json"
            },
            Body = data
        })
        if response and response.Body then
            return true, response.Body
        elseif response and response.Success and response.ResponseBody then
            return true, response.ResponseBody
        end
        return false, "Exploit HTTP request failed"
    end
    return false, "No supported exploit HTTP request function found"
end


local function validateKey(key)
    local hwid = getSystemHWID()
    

    local executor = identifyexecutor()
    

    local requestData = {
        key = key,
        hwid = hwid,
        executor = executor
    }
    

    local jsonData = HttpService:JSONEncode(requestData)
    
    local success, response = sendHttpPost(API_URL, jsonData)
    
    if not success then
        return false, "Failed to connect to validation server: " .. tostring(response)
    end
    

    local decoded = HttpService:JSONDecode(response)
    
    if not decoded.valid then
        return false, "Invalid key"
    end
    
    if not decoded.hwid_match then
        return false, "HWID mismatch - key is bound to a different machine"
    end
    
    return true, "Key validated successfully"
end


local function main()
    local key = getgenv().script_key
    if not key then
        error("No key found, fix it stupid")
    end
    
    local success, message = validateKey(key)
    if success then
        print("✓ Authentication successful:", message)
    else
        print("✗ Authentication failed:", message)
        game.Players.LocalPlayer:Kick("This key is blacklisted or doesn't exist. Please contact @pharanoh if you believe this is a mistake")
    end
end


main()


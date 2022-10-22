

function NTCyb.UpdateHuman(character)

    local velocity = 0
    if 
        character ~= nil and 
        character.AnimController ~= nil and 
        character.AnimController.MainLimb ~= nil and 
        character.AnimController.MainLimb.body ~= nil and 
        character.AnimController.MainLimb.body.LinearVelocity ~= nil then
            velocity = character.AnimController.MainLimb.body.LinearVelocity.Length() end

    local function updateLimb(character,limbtype) 
        if not NTCyb.HF.LimbIsCyber(character,limbtype) then return end
        NTCyb.ConvertDamageTypes(character,limbtype)

        local limb = character.AnimController.GetLimb(limbtype)

        -- cyber stats
        local loosescrews = HF.GetAfflictionStrengthLimb(character,limbtype,"ntc_loosescrews",0)
        local damagedelectronics = HF.GetAfflictionStrengthLimb(character,limbtype,"ntc_damagedelectronics",0)
        local bentmetal = HF.GetAfflictionStrengthLimb(character,limbtype,"ntc_bentmetal",0)
        local materialloss = HF.GetAfflictionStrengthLimb(character,limbtype,"ntc_materialloss",0)
    
        -- water damage if unprotected
        if character.PressureProtection <= 1000 then
            -- in water?
            local inwater = false
            if limb~=nil and limb.InWater then inwater=true end
            if inwater then
                -- add damaged electronics
                Timer.Wait(function(limb)
                    if limb ~= nil then
                        local spawnpos = limb.WorldPosition
                        HF.SpawnItemAt("ntcvfx_malfunction",spawnpos) end
                end,math.random(1,500))
                HF.AddAfflictionLimb(character,"ntc_damagedelectronics",limbtype,2*(1+loosescrews/100)*(1+materialloss/100)*NT.Deltatime)
            end
        end

        -- moving around damages if loose screws high enough
        if loosescrews > 30 and velocity > 1 then
            HF.AddAfflictionLimb(character,"ntc_materialloss",limbtype,HF.Clamp(velocity,0,5)*(loosescrews/500)*NT.Deltatime)
            HF.AddAfflictionLimb(character,"ntc_loosescrews",limbtype,HF.Clamp(velocity,0,5)/50*NT.Deltatime)
        end
        

        -- losing the limb
        if materialloss >= 99 then
            NTCyb.UncyberifyLimb(character,limbtype)
            NT.TraumamputateLimbMinusItem(character,limbtype)
            HF.GiveItem(character,"ntcsfx_cyberdeath")
            HF.AddAfflictionLimb(character,"internaldamage",limbtype,HF.RandomRange(30,60))
            HF.AddAfflictionLimb(character,"foreignbody",limbtype,HF.RandomRange(10,25))
            return
        end

        -- limb malfunction due to damaged electronics
        local malfunction = (damagedelectronics > 20 and HF.Chance((damagedelectronics/120)^4))
        if malfunction then
            HF.SpawnItemAt("ntcvfx_malfunction",limb.WorldPosition)
        end
        local locklimb = damagedelectronics >= 99 or bentmetal >= 99 or malfunction
            
        local function lockLimb()
            local limbIdentifierLookup = {}
            limbIdentifierLookup[LimbType.LeftArm] = "lockleftarm"
            limbIdentifierLookup[LimbType.RightArm] = "lockrightarm"
            limbIdentifierLookup[LimbType.LeftLeg] = "lockleftleg"
            limbIdentifierLookup[LimbType.RightLeg] = "lockrightleg"
            if limbIdentifierLookup[limbtype]==nil then return end
            NTC.SetSymptomTrue(character,limbIdentifierLookup[limbtype])
        end

        if locklimb then lockLimb() end

        -- slowdown due to bent metal
        if bentmetal > 5 and (limbtype == LimbType.LeftLeg or limbtype==LimbType.RightLeg) then
            NTC.MultiplySpeed(character,1-(bentmetal/100)*0.5)
        end
    end
    
    updateLimb(character,LimbType.Torso)
    updateLimb(character,LimbType.Head)
    updateLimb(character,LimbType.LeftLeg)
    updateLimb(character,LimbType.RightLeg)
    updateLimb(character,LimbType.LeftArm)
    updateLimb(character,LimbType.RightArm)

end

function NTCyb.ConvertDamageTypes(character,limbtype)

    -- local function isExtremity() 
    --     return not limbtype==LimbType.Torso and not limbtype==LimbType.Head
    -- end

    if NTCyb.HF.LimbIsCyber(character,limbtype) then
        
        -- /// fetch stats ///

        -- physical damage types
        local bleeding = HF.GetAfflictionStrengthLimb(character,limbtype,"bleeding",0)
        local burn = HF.GetAfflictionStrengthLimb(character,limbtype,"burn",0)
        local lacerations = HF.GetAfflictionStrengthLimb(character,limbtype,"lacerations",0)
        local gunshotwound = HF.GetAfflictionStrengthLimb(character,limbtype,"gunshotwound",0)
        local bitewounds = HF.GetAfflictionStrengthLimb(character,limbtype,"bitewounds",0)
        local explosiondamage = HF.GetAfflictionStrengthLimb(character,limbtype,"explosiondamage",0)
        local blunttrauma = HF.GetAfflictionStrengthLimb(character,limbtype,"blunttrauma",0)
        local internaldamage = HF.GetAfflictionStrengthLimb(character,limbtype,"internaldamage",0)
        local foreignbody = HF.GetAfflictionStrengthLimb(character,limbtype,"foreignbody",0)

        -- cyber stats
        local loosescrews = HF.GetAfflictionStrengthLimb(character,limbtype,"ntc_loosescrews",0)
        local prevloosescrews = loosescrews
        local damagedelectronics = HF.GetAfflictionStrengthLimb(character,limbtype,"ntc_damagedelectronics",0)
        local prevdamagedelectronics = damagedelectronics
        local bentmetal = HF.GetAfflictionStrengthLimb(character,limbtype,"ntc_bentmetal",0)
        local prevbentmetal = bentmetal
        local materialloss = HF.GetAfflictionStrengthLimb(character,limbtype,"ntc_materialloss",0)
        local prevmaterialloss = materialloss

        -- calculate damage conversion

        local function damageChance(val,chance)
            if val > 0.01 and HF.Chance(chance) then return val end
            return 0
        end

        loosescrews = loosescrews + 1*(
            0.25*damageChance(lacerations,0.75)+
            1*damageChance(explosiondamage,0.8)+
            0.5*damageChance(blunttrauma,0.5)+
            1*damageChance(internaldamage,0.75)+
            0.5*damageChance(bitewounds,0.5)+
            0.75*damageChance(foreignbody,0.75))

        damagedelectronics = damagedelectronics + 0.5*(1+prevmaterialloss/50)*(
            2*damageChance(burn,0.75)+
            0.75*damageChance(gunshotwound,0.85)+
            0.25*damageChance(bitewounds,0.5)+
            0.5*damageChance(explosiondamage,0.5)+
            1*damageChance(blunttrauma,0.5)+
            1*damageChance(internaldamage,0.75)+
            0.75*damageChance(foreignbody,0.75))

        bentmetal = bentmetal + 1*(
            0.25*damageChance(burn,0.85)+
            0.25*damageChance(lacerations,0.5)+
            0.5*damageChance(bitewounds,0.5)+
            1*damageChance(explosiondamage,0.85)+
            2*damageChance(blunttrauma,0.75))

        materialloss = materialloss + (1+prevloosescrews/50)*(
            0.5*damageChance(lacerations,0.75)+
            0.8*damageChance(gunshotwound,0.8)+
            0.6*damageChance(bitewounds,0.75)+
            1*explosiondamage+
            0.5*damageChance(foreignbody,0.8))


        -- /// apply changes ///

        HF.ApplyAfflictionChangeLimb(character,limbtype,"burn",0,burn,0,200)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"bleeding",0,bleeding,0,100)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"lacerations",0,lacerations,0,200)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"gunshotwound",0,gunshotwound,0,200)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"bitewounds",0,bitewounds,0,200)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"explosiondamage",0,explosiondamage,0,200)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"blunttrauma",0,blunttrauma,0,200)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"internaldamage",0,internaldamage,0,200)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"foreignbody",0,foreignbody,0,100)
        
        HF.ApplyAfflictionChangeLimb(character,limbtype,"ntc_loosescrews",loosescrews,prevloosescrews,0,100)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"ntc_damagedelectronics",damagedelectronics,prevdamagedelectronics,0,100)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"ntc_bentmetal",bentmetal,prevbentmetal,0,100)
        HF.ApplyAfflictionChangeLimb(character,limbtype,"ntc_materialloss",materialloss,prevmaterialloss,0,100)

        HF.SetAfflictionLimb(character,"dislocation1",limbtype,0)
        HF.SetAfflictionLimb(character,"dislocation2",limbtype,0)
        HF.SetAfflictionLimb(character,"dislocation3",limbtype,0)
        HF.SetAfflictionLimb(character,"dislocation4",limbtype,0)

        HF.SetAfflictionLimb(character,"ll_arterialcut",limbtype,0)
        HF.SetAfflictionLimb(character,"rl_arterialcut",limbtype,0)
        HF.SetAfflictionLimb(character,"la_arterialcut",limbtype,0)
        HF.SetAfflictionLimb(character,"ra_arterialcut",limbtype,0)
        HF.SetAfflictionLimb(character,"h_arterialcut",limbtype,0)
        HF.SetAfflictionLimb(character,"t_arterialcut",limbtype,0)

        HF.SetAfflictionLimb(character,"tll_amputation",limbtype,0)
        HF.SetAfflictionLimb(character,"trl_amputation",limbtype,0)
        HF.SetAfflictionLimb(character,"tla_amputation",limbtype,0)
        HF.SetAfflictionLimb(character,"tra_amputation",limbtype,0)

    end
end
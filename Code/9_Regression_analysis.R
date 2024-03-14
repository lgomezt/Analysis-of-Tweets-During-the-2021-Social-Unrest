rm(list = ls()) 

library(pacman)
p_load("tidyverse", "rstudioapi", "lubridate", "lmtest", "sandwich",
       "lfe", "stargazer")

# Definir directorio
script_path <- dirname(rstudioapi::getSourceEditorContext()$path)
setwd(script_path)

# Importar datos
df <- read_delim("proximidad.csv", delim = ";")

# Definir los días críticos
dias_criticos <- as.Date(c('2021-04-28', '2021-05-03', '2021-05-04', '2021-05-05', 
                           '2021-06-20', '2021-05-01', '2021-06-28', '2021-05-09'))

# Asegurarse de que la columna 'Date' esté en formato fecha
df$Date <- as.Date(df$Date)

# Crear las variables t0_critico y t1_critico
t0_critico <- dias_criticos
t1_critico <- t0_critico + days(1) # Añade un día a cada fecha en t0_critico

# Crear columnas lógicas que indican si 'Date' está en t0_critico o t1_critico
df$t0_critico <- df$Date %in% t0_critico
df$t1_critico <- df$Date %in% t1_critico

# Añadir número del día de la semana (lunes = 1)
df$day_number <- wday(df$Date) 

# Convertir day_number a factor
df$day_number <- as.factor(df$day_number)

# Convertir Nodo_ID a factor
df$Nodo_ID <- as.factor(df$Nodo_ID)

# Ahora vamos a construir las interacciones
df["t0_izq"] <- df$t0_critico * (df$Political_Affiliation == "Izquierda")
df["t0_der"] <- df$t0_critico * (df$Political_Affiliation == "Derecha")
df["t0_cen"] <- df$t0_critico * (df$Political_Affiliation == "Centro")
df["t0_sc"] <- df$t0_critico * (df$Political_Affiliation == "Sin Clasificar")
df["t1_izq"] <- df$t1_critico * (df$Political_Affiliation == "Izquierda")
df["t1_der"] <- df$t1_critico * (df$Political_Affiliation == "Derecha")
df["t1_cen"] <- df$t1_critico * (df$Political_Affiliation == "Centro")
df["t1_sc"] <- df$t1_critico * (df$Political_Affiliation == "Sin Clasificar")

df$Political_Affiliation <- as.factor(df$Political_Affiliation)
df$t0_critico <- as.numeric(df$t0_critico)
df$t1_critico <- as.numeric(df$t1_critico)

# Crear una columna lógica para indicar los fines de semana
df$weekend <- df$day_number %in% c(6, 7)


# Total RTs vs PA ---------------------------------------------------------
# 2. Sin Efectos Fijos, sin PA
modelo1 <- lm(Total_RTs ~ t0_critico, data = df)
modelo2 <- lm(Total_RTs ~ t0_critico + t1_critico, data = df)
modelo3 <- lm(Total_RTs ~ t0_critico + t1_critico + weekend, data = df)
modelo4 <- lm(Total_RTs ~ t0_critico + t1_critico + day_number, data = df)

stargazer(modelo1, modelo2, modelo3, modelo4, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Total RTs",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 3. Con Efectos Fijos, sin PA
modelo1_fe <- felm(Total_RTs ~ t0_critico | Nodo_ID, data = df)
modelo2_fe <- felm(Total_RTs ~ t0_critico + t1_critico | Nodo_ID, data = df)
modelo3_fe <- felm(Total_RTs ~ t0_critico + t1_critico + weekend | Nodo_ID, data = df)
modelo4_fe <- felm(Total_RTs ~ t0_critico + t1_critico + day_number | Nodo_ID, data = df)

stargazer(modelo1_fe, modelo2_fe, modelo3_fe, modelo4_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Total RTs",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# 4. Sin efectos fijos, con PA
modelo5 <- lm(Total_RTs ~ -1 + t0_critico + Political_Affiliation, data = df)
modelo6 <- lm(Total_RTs ~ -1 + t0_critico + t1_critico + Political_Affiliation, data = df)
modelo7 <- lm(Total_RTs ~ -1 + t0_critico + t1_critico + Political_Affiliation + weekend, data = df)
modelo8 <- lm(Total_RTs ~ -1 + t0_critico + t1_critico + Political_Affiliation + day_number, data = df)

stargazer(modelo5, modelo6, modelo7, modelo8, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Total RTs",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Political Affiliation: Center", 
                               "Political Affiliation: Right", 
                               "Political Affiliation: Left", 
                               "Political Affiliation: Unknown", 
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 5. Con efectos fijos, con PA
modelo5_fe <- felm(Total_RTs ~ t0_critico + Political_Affiliation | Nodo_ID, data = df)
modelo6_fe <- felm(Total_RTs ~ t0_critico + t1_critico + Political_Affiliation | Nodo_ID, data = df)
modelo7_fe <- felm(Total_RTs ~ t0_critico + t1_critico + Political_Affiliation + weekend | Nodo_ID, data = df)
modelo8_fe <- felm(Total_RTs ~ t0_critico + t1_critico + Political_Affiliation + day_number | Nodo_ID, data = df)

stargazer(modelo5_fe, modelo6_fe, modelo7_fe, modelo8_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Total RTs",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               # "Political Affiliation: Center", 
                               "Political Affiliation: Right", 
                               "Political Affiliation: Left", 
                               "Political Affiliation: Unknown", 
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# Total RTs vs PA con interacción -----------------------------------------
# 6. Total RTs vs Critical day interactuado con PA, sin FE
modelo9 <- lm(Total_RTs ~ t0_izq + t0_der + t0_cen + t0_sc + weekend, data = df)
modelo10 <- lm(Total_RTs ~ t0_izq + t0_der + t0_cen + t0_sc + day_number, data = df)
modelo11 <- lm(Total_RTs ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend, data = df)
modelo12 <- lm(Total_RTs ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number, data = df)

stargazer(modelo9, modelo10, modelo11, modelo12, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Total RTs",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 7. Total RTs vs Critical day interactuado con PA, con FE
modelo9_fe <- felm(Total_RTs ~ t0_izq + t0_der + t0_cen + t0_sc + weekend | Nodo_ID, data = df)
modelo10_fe <- felm(Total_RTs ~ t0_izq + t0_der + t0_cen + t0_sc + day_number | Nodo_ID, data = df)
modelo11_fe <- felm(Total_RTs ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend | Nodo_ID, data = df)
modelo12_fe <- felm(Total_RTs ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number | Nodo_ID, data = df)

stargazer(modelo9_fe, modelo10_fe, modelo11_fe, modelo12_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Total RTs",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# Inner Proximity vs PA -----------------------------------------------------
# 8. Inner Proximity vs critical day sin FE
modelo13 <- lm(P_Mismo ~ t0_critico, data = df)
modelo14 <- lm(P_Mismo ~ t0_critico + t1_critico, data = df)
modelo15 <- lm(P_Mismo ~ t0_critico + t1_critico + weekend, data = df)
modelo16 <- lm(P_Mismo ~ t0_critico + t1_critico + day_number, data = df)

stargazer(modelo13, modelo14, modelo15, modelo16, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Inner Proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 9. Inner Proximity vs critical day con FE
modelo13_fe <- felm(P_Mismo ~ t0_critico | Nodo_ID, data = df)
modelo14_fe <- felm(P_Mismo ~ t0_critico + t1_critico | Nodo_ID, data = df)
modelo15_fe <- felm(P_Mismo ~ t0_critico + t1_critico + weekend | Nodo_ID, data = df)
modelo16_fe <- felm(P_Mismo ~ t0_critico + t1_critico + day_number | Nodo_ID, data = df)

stargazer(modelo13_fe, modelo14_fe, modelo15_fe, modelo16_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Inner Proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# 10. Inner Proximity vs Critical day, con PA, sin FE
modelo17 <- lm(P_Mismo ~ -1 + t0_critico + Political_Affiliation, data = df)
modelo18 <- lm(P_Mismo ~ -1 + t0_critico + t1_critico + Political_Affiliation, data = df)
modelo19 <- lm(P_Mismo ~ -1 + t0_critico + t1_critico + Political_Affiliation + weekend, data = df)
modelo20 <- lm(P_Mismo ~ -1 + t0_critico + t1_critico + Political_Affiliation + day_number, data = df)

stargazer(modelo17, modelo18, modelo19, modelo20, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Inner Proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Political Affiliation: Center", 
                               "Political Affiliation: Right", 
                               "Political Affiliation: Left", 
                               "Political Affiliation: Unknown", 
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# Inner Proximity vs PA con interacción -----------------------------------
# 11. Inner Proximity vs Critical day interactuado con PA, sin FE
modelo21 <- lm(P_Mismo ~ t0_izq + t0_der + t0_cen + t0_sc + weekend, data = df)
modelo22 <- lm(P_Mismo ~ t0_izq + t0_der + t0_cen + t0_sc + day_number, data = df)
modelo23 <- lm(P_Mismo ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend, data = df)
modelo24 <- lm(P_Mismo ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number, data = df)

stargazer(modelo21, modelo22, modelo23, modelo24, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Inner Proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 12. Inner Proximity vs Critical day interactuado con PA, con FE
modelo21_fe <- felm(P_Mismo ~ t0_izq + t0_der + t0_cen + t0_sc + weekend | Nodo_ID, data = df)
modelo22_fe <- felm(P_Mismo ~ t0_izq + t0_der + t0_cen + t0_sc + day_number | Nodo_ID, data = df)
modelo23_fe <- felm(P_Mismo ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend | Nodo_ID, data = df)
modelo24_fe <- felm(P_Mismo ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number | Nodo_ID, data = df)

stargazer(modelo21_fe, modelo22_fe, modelo23_fe, modelo24_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Inner Proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# Outer proximity vs PA ---------------------------------------------------
# 13. Outer Proximity vs critical day sin FE
modelo25 <- lm(P_Otros ~ t0_critico, data = df)
modelo26 <- lm(P_Otros ~ t0_critico + t1_critico, data = df)
modelo27 <- lm(P_Otros ~ t0_critico + t1_critico + weekend, data = df)
modelo28 <- lm(P_Otros ~ t0_critico + t1_critico + day_number, data = df)

stargazer(modelo25, modelo26, modelo27, modelo28, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Outer Proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 14. Outer Proximity vs critical day con FE
modelo25_fe <- felm(P_Otros ~ t0_critico | Nodo_ID, data = df)
modelo26_fe <- felm(P_Otros ~ t0_critico + t1_critico | Nodo_ID, data = df)
modelo27_fe <- felm(P_Otros ~ t0_critico + t1_critico + weekend | Nodo_ID, data = df)
modelo28_fe <- felm(P_Otros ~ t0_critico + t1_critico + day_number | Nodo_ID, data = df)

stargazer(modelo25_fe, modelo26_fe, modelo27_fe, modelo28_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Outer proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# 15. Outer Proximity vs Critical day, con PA, sin FE
modelo29 <- lm(P_Otros ~ -1 + t0_critico + Political_Affiliation, data = df)
modelo30 <- lm(P_Otros ~ -1 + t0_critico + t1_critico + Political_Affiliation, data = df)
modelo31 <- lm(P_Otros ~ -1 + t0_critico + t1_critico + Political_Affiliation + weekend, data = df)
modelo32 <- lm(P_Otros ~ -1 + t0_critico + t1_critico + Political_Affiliation + day_number, data = df)

stargazer(modelo29, modelo30, modelo31, modelo32, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Outer Proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Political Affiliation: Center", 
                               "Political Affiliation: Right", 
                               "Political Affiliation: Left", 
                               "Political Affiliation: Unknown", 
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# Outer proximity vs PA con interacción -----------------------------------
# 16. Outer Proximity vs Critical day interactuado con PA, sin FE
modelo33 <- lm(P_Otros ~ t0_izq + t0_der + t0_cen + t0_sc + weekend, data = df)
modelo34 <- lm(P_Otros ~ t0_izq + t0_der + t0_cen + t0_sc + day_number, data = df)
modelo35 <- lm(P_Otros ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend, data = df)
modelo36 <- lm(P_Otros ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number, data = df)

stargazer(modelo33, modelo34, modelo35, modelo36, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Outer Proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 17. Outer Proximity vs Critical day interactuado con PA, con FE
modelo33_fe <- felm(P_Otros ~ t0_izq + t0_der + t0_cen + t0_sc + weekend | Nodo_ID, data = df)
modelo34_fe <- felm(P_Otros ~ t0_izq + t0_der + t0_cen + t0_sc + day_number | Nodo_ID, data = df)
modelo35_fe <- felm(P_Otros ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend | Nodo_ID, data = df)
modelo36_fe <- felm(P_Otros ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number | Nodo_ID, data = df)

stargazer(modelo33_fe, modelo34_fe, modelo35_fe, modelo36_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Outer Proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# Left proximity vs PA ---------------------------------------------------
# 18. Left Proximity vs critical day sin FE
modelo37 <- lm(P_Izquierda ~ t0_critico, data = df)
modelo38 <- lm(P_Izquierda ~ t0_critico + t1_critico, data = df)
modelo39 <- lm(P_Izquierda ~ t0_critico + t1_critico + weekend, data = df)
modelo40 <- lm(P_Izquierda ~ t0_critico + t1_critico + day_number, data = df)

stargazer(modelo37, modelo38, modelo39, modelo40, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Left Proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 19. Left Proximity vs critical day con FE
modelo37_fe <- felm(P_Izquierda ~ t0_critico | Nodo_ID, data = df)
modelo38_fe <- felm(P_Izquierda ~ t0_critico + t1_critico | Nodo_ID, data = df)
modelo39_fe <- felm(P_Izquierda ~ t0_critico + t1_critico + weekend | Nodo_ID, data = df)
modelo40_fe <- felm(P_Izquierda ~ t0_critico + t1_critico + day_number | Nodo_ID, data = df)

stargazer(modelo37_fe, modelo38_fe, modelo39_fe, modelo40_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Left proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# 20. Left Proximity vs Critical day, con PA, sin FE
modelo41 <- lm(P_Izquierda ~ -1 + t0_critico + Political_Affiliation, data = df)
modelo42 <- lm(P_Izquierda ~ -1 + t0_critico + t1_critico + Political_Affiliation, data = df)
modelo43 <- lm(P_Izquierda ~ -1 + t0_critico + t1_critico + Political_Affiliation + weekend, data = df)
modelo44 <- lm(P_Izquierda ~ -1 + t0_critico + t1_critico + Political_Affiliation + day_number, data = df)

stargazer(modelo41, modelo42, modelo43, modelo44, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Left Proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Political Affiliation: Center", 
                               "Political Affiliation: Right", 
                               "Political Affiliation: Left", 
                               "Political Affiliation: Unknown", 
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# Left proximity vs PA con interacción -----------------------------------
# 21. Left Proximity vs Critical day interactuado con PA, sin FE
modelo45 <- lm(P_Izquierda ~ t0_izq + t0_der + t0_cen + t0_sc + weekend, data = df)
modelo46 <- lm(P_Izquierda ~ t0_izq + t0_der + t0_cen + t0_sc + day_number, data = df)
modelo47 <- lm(P_Izquierda ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend, data = df)
modelo48 <- lm(P_Izquierda ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number, data = df)

stargazer(modelo45, modelo46, modelo47, modelo48, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Left Proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 22. Left Proximity vs Critical day interactuado con PA, con FE
modelo45_fe <- felm(P_Izquierda ~ t0_izq + t0_der + t0_cen + t0_sc + weekend | Nodo_ID, data = df)
modelo46_fe <- felm(P_Izquierda ~ t0_izq + t0_der + t0_cen + t0_sc + day_number | Nodo_ID, data = df)
modelo47_fe <- felm(P_Izquierda ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend | Nodo_ID, data = df)
modelo48_fe <- felm(P_Izquierda ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number | Nodo_ID, data = df)

stargazer(modelo45_fe, modelo46_fe, modelo47_fe, modelo48_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Left Proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# Right proximity vs PA ---------------------------------------------------
# 23. Right Proximity vs critical day sin FE
modelo49 <- lm(P_Derecha ~ t0_critico, data = df)
modelo50 <- lm(P_Derecha ~ t0_critico + t1_critico, data = df)
modelo51 <- lm(P_Derecha ~ t0_critico + t1_critico + weekend, data = df)
modelo52 <- lm(P_Derecha ~ t0_critico + t1_critico + day_number, data = df)

stargazer(modelo49, modelo50, modelo51, modelo52, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Right Proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 24. Right Proximity vs critical day con FE
modelo49_fe <- felm(P_Derecha ~ t0_critico | Nodo_ID, data = df)
modelo50_fe <- felm(P_Derecha ~ t0_critico + t1_critico | Nodo_ID, data = df)
modelo51_fe <- felm(P_Derecha ~ t0_critico + t1_critico + weekend | Nodo_ID, data = df)
modelo52_fe <- felm(P_Derecha ~ t0_critico + t1_critico + day_number | Nodo_ID, data = df)

stargazer(modelo49_fe, modelo50_fe, modelo51_fe, modelo52_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Right proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# 25. Right Proximity vs Critical day, con PA, sin FE
modelo53 <- lm(P_Derecha ~ -1 + t0_critico + Political_Affiliation, data = df)
modelo54 <- lm(P_Derecha ~ -1 + t0_critico + t1_critico + Political_Affiliation, data = df)
modelo55 <- lm(P_Derecha ~ -1 + t0_critico + t1_critico + Political_Affiliation + weekend, data = df)
modelo56 <- lm(P_Derecha ~ -1 + t0_critico + t1_critico + Political_Affiliation + day_number, data = df)

stargazer(modelo53, modelo54, modelo55, modelo56, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Right Proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Political Affiliation: Center", 
                               "Political Affiliation: Right", 
                               "Political Affiliation: Left", 
                               "Political Affiliation: Unknown", 
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# Right proximity vs PA con interacción -----------------------------------
# 26. Right Proximity vs Critical day interactuado con PA, sin FE
modelo57 <- lm(P_Derecha ~ t0_izq + t0_der + t0_cen + t0_sc + weekend, data = df)
modelo58 <- lm(P_Derecha ~ t0_izq + t0_der + t0_cen + t0_sc + day_number, data = df)
modelo59 <- lm(P_Derecha ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend, data = df)
modelo60 <- lm(P_Derecha ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number, data = df)

stargazer(modelo57, modelo58, modelo59, modelo60, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Right Proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 27. Right Proximity vs Critical day interactuado con PA, con FE
modelo61_fe <- felm(P_Derecha ~ t0_izq + t0_der + t0_cen + t0_sc + weekend | Nodo_ID, data = df)
modelo62_fe <- felm(P_Derecha ~ t0_izq + t0_der + t0_cen + t0_sc + day_number | Nodo_ID, data = df)
modelo63_fe <- felm(P_Derecha ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend | Nodo_ID, data = df)
modelo64_fe <- felm(P_Derecha ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number | Nodo_ID, data = df)

stargazer(modelo61_fe, modelo62_fe, modelo63_fe, modelo64_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Right Proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# Center proximity vs PA ---------------------------------------------------
# 28. Center proximity vs critical day sin FE
modelo65 <- lm(P_Centro ~ t0_critico, data = df)
modelo66 <- lm(P_Centro ~ t0_critico + t1_critico, data = df)
modelo67 <- lm(P_Centro ~ t0_critico + t1_critico + weekend, data = df)
modelo68 <- lm(P_Centro ~ t0_critico + t1_critico + day_number, data = df)

stargazer(modelo65, modelo66, modelo67, modelo68, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Center proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 29. Center proximity vs critical day con FE
modelo65_fe <- felm(P_Centro ~ t0_critico | Nodo_ID, data = df)
modelo66_fe <- felm(P_Centro ~ t0_critico + t1_critico | Nodo_ID, data = df)
modelo67_fe <- felm(P_Centro ~ t0_critico + t1_critico + weekend | Nodo_ID, data = df)
modelo68_fe <- felm(P_Centro ~ t0_critico + t1_critico + day_number | Nodo_ID, data = df)

stargazer(modelo65_fe, modelo66_fe, modelo67_fe, modelo68_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Center proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# 30. Center proximity vs Critical day, con PA, sin FE
modelo69 <- lm(P_Centro ~ -1 + t0_critico + Political_Affiliation, data = df)
modelo70 <- lm(P_Centro ~ -1 + t0_critico + t1_critico + Political_Affiliation, data = df)
modelo71 <- lm(P_Centro ~ -1 + t0_critico + t1_critico + Political_Affiliation + weekend, data = df)
modelo72 <- lm(P_Centro ~ -1 + t0_critico + t1_critico + Political_Affiliation + day_number, data = df)

stargazer(modelo69, modelo70, modelo71, modelo72, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Center proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Political Affiliation: Center", 
                               "Political Affiliation: Right", 
                               "Political Affiliation: Left", 
                               "Political Affiliation: Unknown", 
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# Center proximity vs PA con interacción -----------------------------------
# 31. Center proximity vs Critical day interactuado con PA, sin FE
modelo73 <- lm(P_Centro ~ t0_izq + t0_der + t0_cen + t0_sc + weekend, data = df)
modelo74 <- lm(P_Centro ~ t0_izq + t0_der + t0_cen + t0_sc + day_number, data = df)
modelo75 <- lm(P_Centro ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend, data = df)
modelo76 <- lm(P_Centro ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number, data = df)

stargazer(modelo73, modelo74, modelo75, modelo76, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Center proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 32. Center proximity vs Critical day interactuado con PA, con FE
modelo73_fe <- felm(P_Centro ~ t0_izq + t0_der + t0_cen + t0_sc + weekend | Nodo_ID, data = df)
modelo74_fe <- felm(P_Centro ~ t0_izq + t0_der + t0_cen + t0_sc + day_number | Nodo_ID, data = df)
modelo75_fe <- felm(P_Centro ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend | Nodo_ID, data = df)
modelo76_fe <- felm(P_Centro ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number | Nodo_ID, data = df)

stargazer(modelo73_fe, modelo74_fe, modelo75_fe, modelo76_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Center proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# Unknown proximity vs PA ---------------------------------------------------
# 33. Unknown proximity vs critical day sin FE
modelo77 <- lm(`P_Sin Clasificar` ~ t0_critico, data = df)
modelo78 <- lm(`P_Sin Clasificar` ~ t0_critico + t1_critico, data = df)
modelo79 <- lm(`P_Sin Clasificar` ~ t0_critico + t1_critico + weekend, data = df)
modelo80 <- lm(`P_Sin Clasificar` ~ t0_critico + t1_critico + day_number, data = df)

stargazer(modelo77, modelo78, modelo79, modelo80, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Unknown proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 34. Unknown proximity vs critical day con FE
modelo77_fe <- felm(`P_Sin Clasificar` ~ t0_critico | Nodo_ID, data = df)
modelo78_fe <- felm(`P_Sin Clasificar` ~ t0_critico + t1_critico | Nodo_ID, data = df)
modelo79_fe <- felm(`P_Sin Clasificar` ~ t0_critico + t1_critico + weekend | Nodo_ID, data = df)
modelo80_fe <- felm(`P_Sin Clasificar` ~ t0_critico + t1_critico + day_number | Nodo_ID, data = df)

stargazer(modelo77_fe, modelo78_fe, modelo79_fe, modelo80_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Unknown proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

# 35. Unknown proximity vs Critical day, con PA, sin FE
modelo81 <- lm(`P_Sin Clasificar` ~ -1 + t0_critico + Political_Affiliation, data = df)
modelo82 <- lm(`P_Sin Clasificar` ~ -1 + t0_critico + t1_critico + Political_Affiliation, data = df)
modelo83 <- lm(`P_Sin Clasificar` ~ -1 + t0_critico + t1_critico + Political_Affiliation + weekend, data = df)
modelo84 <- lm(`P_Sin Clasificar` ~ -1 + t0_critico + t1_critico + Political_Affiliation + day_number, data = df)

stargazer(modelo81, modelo82, modelo83, modelo84, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Unknown proximity",
          covariate.labels = c("Critical day (t)", "Critical day (t+1)",
                               "Political Affiliation: Center", 
                               "Political Affiliation: Right", 
                               "Political Affiliation: Left", 
                               "Political Affiliation: Unknown", 
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# Unknown proximity vs PA con interacción -----------------------------------
# 36. Unknown proximity vs Critical day interactuado con PA, sin FE
modelo85 <- lm(`P_Sin Clasificar` ~ t0_izq + t0_der + t0_cen + t0_sc + weekend, data = df)
modelo86 <- lm(`P_Sin Clasificar` ~ t0_izq + t0_der + t0_cen + t0_sc + day_number, data = df)
modelo87 <- lm(`P_Sin Clasificar` ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend, data = df)
modelo88 <- lm(`P_Sin Clasificar` ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number, data = df)

stargazer(modelo85, modelo86, modelo87, modelo88, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Unknown proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("No", 4))))

# 37. Unknown proximity vs Critical day interactuado con PA, con FE
modelo85_fe <- felm(`P_Sin Clasificar` ~ t0_izq + t0_der + t0_cen + t0_sc + weekend | Nodo_ID, data = df)
modelo86_fe <- felm(`P_Sin Clasificar` ~ t0_izq + t0_der + t0_cen + t0_sc + day_number | Nodo_ID, data = df)
modelo87_fe <- felm(`P_Sin Clasificar` ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + weekend | Nodo_ID, data = df)
modelo88_fe <- felm(`P_Sin Clasificar` ~ t0_izq + t0_der + t0_cen + t0_sc + t1_izq + t1_der + t1_cen + t1_sc + day_number | Nodo_ID, data = df)

stargazer(modelo85_fe, modelo86_fe, modelo87_fe, modelo88_fe, type = "latex",
          dep.var.labels.include = FALSE,
          dep.var.caption = "Unknown proximity",
          covariate.labels = c("Critical day (t) $\\times$ P.A. Left",
                               "Critical day (t) $\\times$ P.A. Right",
                               "Critical day (t) $\\times$ P.A. Center",
                               "Critical day (t) $\\times$ P.A. Unknown",
                               "Critical day (t + 1) $\\times$ P.A. Left",
                               "Critical day (t + 1) $\\times$ P.A. Right",
                               "Critical day (t + 1) $\\times$ P.A. Center",
                               "Critical day (t + 1) $\\times$ P.A. Unknown",
                               "Weekend", "Tuesday", "Wednesday", "Thursday",
                               "Friday", "Saturday", "Sunday", "Constant"),
          add.lines = list(c("Individual FE", rep("Yes", 4))))

